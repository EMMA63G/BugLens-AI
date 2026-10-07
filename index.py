from flask import Flask, render_template_string, request, jsonify
from huggingface_hub import InferenceClient
import os

app = Flask(__name__)

# قالب HTML والتصميم المودرن المتكامل (الفرونت إند الشغال والمظبوط)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl" class="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BugLens AI - مساعد تشخيص الأخطاء</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {
            darkMode: 'class',
            theme: {
                extend: {
                    colors: {
                        darkbg: '#0B0F19',
                        cardbg: '#111827',
                        cardborder: '#1F2937',
                    }
                }
            }
        }
    </script>
    <style>
        @keyframes float {
            0%, 100% { transform: translateY(0px) scale(1); }
            50% { transform: translateY(-12px) scale(1.02); }
        }
        .blob-1 { animation: float 8s ease-in-out infinite; }
        .blob-2 { animation: float 10s ease-in-out infinite reverse; }
    </style>
</head>
<body class="bg-darkbg text-gray-100 min-h-screen relative overflow-x-hidden flex flex-col items-center justify-start p-4 sm:p-6 font-sans">

    <!-- خلفية مضيئة متحركة -->
    <div class="absolute top-10 left-10 w-80 h-80 bg-purple-600/15 rounded-full blur-3xl pointer-events-none blob-1"></div>
    <div class="absolute bottom-10 right-10 w-80 h-80 bg-indigo-600/15 rounded-full blur-3xl pointer-events-none blob-2"></div>

    <div class="relative z-10 w-full max-w-5xl">
        
        <!-- الهيدر -->
        <header class="flex flex-col sm:flex-row justify-between items-center bg-cardbg/90 backdrop-blur-xl border border-cardborder rounded-2xl px-6 py-4 mb-6 shadow-2xl gap-4">
            <div class="flex items-center space-x-3 space-x-reverse">
                <div class="w-12 h-12 rounded-xl bg-gradient-to-tr from-indigo-500 to-purple-600 flex items-center justify-center shadow-lg shadow-indigo-500/30 text-2xl">
                    🐞
                </div>
                <div>
                    <h1 class="font-extrabold text-xl bg-gradient-to-r from-indigo-400 to-purple-400 bg-clip-text text-transparent">BugLens AI</h1>
                    <p class="text-xs text-gray-400">تشخيص ذكي لأخطاء بايثون بتقارير منظمة</p>
                </div>
            </div>
            
            <div class="w-full sm:w-auto flex items-center space-x-2 space-x-reverse">
                <input type="password" id="hfToken" placeholder="أدخل Hugging Face Token (hf_...)" 
                    class="bg-gray-950 border border-gray-700 rounded-xl px-4 py-2 text-xs text-gray-100 focus:outline-none focus:border-indigo-500 w-full sm:w-64 transition">
            </div>
        </header>

        <!-- المحتوى الرئيسي -->
        <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
            
            <!-- يسار: المدخلات -->
            <div class="lg:col-span-5 bg-cardbg border border-cardborder rounded-2xl p-6 shadow-2xl flex flex-col justify-between">
                <div>
                    <div class="flex justify-between items-center mb-4">
                        <span class="text-xs font-bold text-gray-300 uppercase tracking-wider flex items-center gap-2">
                            <span class="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse"></span> محطة إدخال الأخطاء
                        </span>
                        <span class="text-[10px] bg-indigo-500/20 text-indigo-300 px-2.5 py-1 rounded-full font-mono">Qwen2.5-Coder</span>
                    </div>

                    <div class="mb-4">
                        <label class="block text-xs font-semibold text-gray-400 mb-1.5">كود البايثون (Python Code)</label>
                        <textarea id="codeCode" rows="5" 
                            class="w-full bg-gray-950 border border-gray-800 rounded-xl p-3.5 text-xs font-mono text-indigo-200 focus:outline-none focus:border-indigo-500 transition resize-none">user_data = {'name': 'Eman'}
print(user_data['email'])</textarea>
                    </div>

                    <div class="mb-5">
                        <label class="block text-xs font-semibold text-gray-400 mb-1.5">رسالة الخطأ (Error Message)</label>
                        <input type="text" id="errorMsg" value="KeyError: 'email'" 
                            class="w-full bg-gray-950 border border-gray-800 rounded-xl px-4 py-2.5 text-xs font-mono text-red-300 focus:outline-none focus:border-indigo-500 transition">
                    </div>
                </div>

                <div>
                    <button onclick="diagnoseBug()" id="submitBtn" 
                        class="w-full bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white font-bold py-3.5 rounded-xl shadow-lg shadow-indigo-600/30 transition duration-200 flex items-center justify-center space-x-2 space-x-reverse cursor-pointer text-sm">
                        <span>تشخيص الخطأ فوراً 🔍</span>
                    </button>

                    <!-- أمثلة سريعة -->
                    <div class="mt-4 pt-4 border-t border-gray-800">
                        <span class="text-[10px] text-gray-400 block mb-2">جرب أخطاء جاهزة بنقرة واحدة:</span>
                        <div class="grid grid-cols-3 gap-2">
                            <button onclick="loadTest('KeyError')" class="bg-gray-900 hover:bg-gray-800 text-indigo-300 text-xs py-1.5 rounded-lg border border-gray-800 transition">KeyError</button>
                            <button onclick="loadTest('TypeError')" class="bg-gray-900 hover:bg-gray-800 text-indigo-300 text-xs py-1.5 rounded-lg border border-gray-800 transition">TypeError</button>
                            <button onclick="loadTest('ZeroDiv')" class="bg-gray-900 hover:bg-gray-800 text-indigo-300 text-xs py-1.5 rounded-lg border border-gray-800 transition">ZeroDiv</button>
                        </div>
                    </div>
                </div>
            </div>

            <!-- يمين: نتائج التشخيص -->
            <div class="lg:col-span-7 bg-cardbg border border-cardborder rounded-2xl p-6 shadow-2xl flex flex-col justify-center items-center min-h-[450px] relative">
                
                <!-- الحالة الافتراضية -->
                <div id="awaitingState" class="text-center py-12">
                    <div class="w-16 h-16 bg-gray-900 border border-gray-800 rounded-2xl flex items-center justify-center mx-auto mb-4 text-indigo-400 text-2xl shadow-inner">
                        💡
                    </div>
                    <h3 class="font-bold text-gray-200 text-base mb-1">جاهز لاستقبال الكود الخاص بك</h3>
                    <p class="text-xs text-gray-400 max-w-xs mx-auto">أدخل التوكن والكود على اليسار واضغط على زر التشخيص لعرض التقرير الشامل.</p>
                </div>

                <!-- حالة التحميل -->
                <div id="loaderState" class="hidden text-center py-12">
                    <div class="inline-block animate-spin rounded-full h-10 w-10 border-4 border-indigo-500 border-t-transparent mb-4"></div>
                    <h3 class="font-bold text-gray-200 text-sm">جاري تحليل الخطأ بذكاء...</h3>
                    <p class="text-xs text-gray-400 mt-1">الرجاء الانتظار لحظات قليلة.</p>
                </div>

                <!-- حالة عرض النتائج -->
                <div id="resultState" class="hidden w-full space-y-4 text-right" dir="rtl">
                    <div class="flex justify-between items-center border-b border-gray-800 pb-3">
                        <div>
                            <span class="text-[10px] text-gray-400 block">نوع الخطأ (Issue)</span>
                            <h3 id="resIssue" class="font-bold text-indigo-400 text-base"></h3>
                        </div>
                        <div>
                            <span class="text-[10px] text-gray-400 block mb-1">مستوى الخطورة</span>
                            <span id="resSeverity" class="px-3 py-1 rounded-full text-xs font-bold bg-red-500/20 text-red-400 border border-red-500/30"></span>
                        </div>
                    </div>

                    <div class="grid grid-cols-2 gap-3 bg-gray-950/60 p-3 rounded-xl border border-gray-800 text-xs">
                        <div>
                            <span class="text-gray-400 block text-[10px]">📍 رقم السطر</span>
                            <span id="resLine" class="font-mono font-bold text-gray-200"></span>
                        </div>
                        <div>
                            <span class="text-gray-400 block text-[10px]">🛠️ السبب الجذري</span>
                            <span id="resRoot" class="text-gray-200 font-medium truncate block"></span>
                        </div>
                    </div>

                    <div>
                        <span class="text-[11px] font-semibold text-gray-400 block mb-1">التفسير التفصيلي</span>
                        <p id="resExp" class="text-xs text-gray-300 bg-gray-950/40 p-3 rounded-xl border border-gray-800 leading-relaxed"></p>
                    </div>

                    <div>
                        <span class="text-[11px] font-semibold text-gray-400 block mb-1">الكود المقترح للإصلاح</span>
                        <pre id="resFix" class="bg-gray-950 p-3 rounded-xl font-mono text-xs text-emerald-300 border border-gray-800 overflow-x-auto text-left" dir="ltr"></pre>
                    </div>

                    <div>
                        <span class="text-[11px] font-semibold text-gray-400 block mb-1">طرق الوقاية المستقبليّة</span>
                        <p id="resPrev" class="text-xs text-indigo-200 bg-indigo-950/20 p-3 rounded-xl border border-indigo-950"></p>
                    </div>
                </div>

            </div>
        </div>
    </div>

    <script>
        function loadTest(type) {
            if (type === 'KeyError') {
                document.getElementById('codeCode').value = "user_data = {'name': 'Eman'}\\nprint(user_data['email'])";
                document.getElementById('errorMsg').value = "KeyError: 'email'";
            } else if (type === 'TypeError') {
                document.getElementById('codeCode').value = "total = 10 + '20'";
                document.getElementById('errorMsg').value = "TypeError: unsupported operand type(s) for +: 'int' and 'str'";
            } else if (type === 'ZeroDiv') {
                document.getElementById('codeCode').value = "result = 100 / 0";
                document.getElementById('errorMsg').value = "ZeroDivisionError: division by zero";
            }
        }

        async function diagnoseBug() {
            const token = document.getElementById('hfToken').value.trim();
            const code = document.getElementById('codeCode').value.trim();
            const error = document.getElementById('errorMsg').value.trim();

            if (!token) {
                alert('⚠️ يرجى إدخال Hugging Face API Token في الأعلى أولاً!');
                return;
            }
            if (!code || !error) {
                alert('الرجاء إدخال الكود ورسالة الخطأ.');
                return;
            }

            document.getElementById('awaitingState').classList.add('hidden');
            document.getElementById('resultState').classList.add('hidden');
            document.getElementById('loaderState').classList.remove('hidden');

            try {
                const response = await fetch('/diagnose', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ token, code, error })
                });

                const data = await response.json();
                document.getElementById('loaderState').classList.add('hidden');

                if (data.success) {
                    const parsed = data.result;
                    document.getElementById('resIssue').innerText = parsed.issue;
                    document.getElementById('resSeverity').innerText = parsed.severity;
                    document.getElementById('resLine').innerText = parsed.line;
                    document.getElementById('resRoot').innerText = parsed.root_cause;
                    document.getElementById('resExp').innerText = parsed.explanation;
                    document.getElementById('resFix').innerText = parsed.suggested_fix;
                    document.getElementById('resPrev').innerText = parsed.prevention;

                    document.getElementById('resultState').classList.remove('hidden');
                } else {
                    document.getElementById('awaitingState').classList.remove('hidden');
                    alert('خطأ: ' + data.error);
                }
            } catch (err) {
                document.getElementById('loaderState').classList.add('hidden');
                document.getElementById('awaitingState').classList.remove('hidden');
                alert('حدث خطأ في الاتصال بالخادم المحلي.');
            }
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/diagnose', methods=['POST'])
def diagnose():
    data = request.json
    token = data.get('token')
    code = data.get('code')
    error = data.get('error')

    try:
        client = InferenceClient(model="Qwen/Qwen2.5-Coder-7B-Instruct", token=token)
        prompt = (
            "You are an expert Senior Software Debugging Engineer. Analyze the following code and error message, "
            "and return ONLY a valid JSON object matching this exact schema:\n"
            "{\n"
            '  "issue": "string",\n'
            '  "severity": "string",\n'
            '  "line": 0,\n'
            '  "root_cause": "string",\n'
            '  "explanation": "string",\n'
            '  "suggested_fix": "string",\n'
            '  "prevention": "string"\n'
            "}\n\n"
            "Code:\n" + code + "\n\n"
            "Error Message:\n" + error + "\n\n"
            "Return ONLY the pure JSON object without any extra text or markdown formatting."
        )

        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            max_tokens=600,
            temperature=0.1
        )

        raw_output = response.choices[0].message.content.strip()
        if raw_output.startswith("```json"):
            raw_output = raw_output[7:]
        if raw_output.endswith("```"):
            raw_output = raw_output[:-3]

        import json
        parsed_json = json.loads(raw_output.strip())
        return jsonify({"success": True, "result": parsed_json})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

if __name__ == '__main__':
    app.run(debug=True, port=5000)