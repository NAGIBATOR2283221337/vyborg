document.addEventListener('DOMContentLoaded', function() {

    // Обновление значений слайдеров
    function updateSliderValue(sliderId, displayId) {
        const slider = document.getElementById(sliderId);
        const display = document.getElementById(displayId);

        slider.addEventListener('input', function() {
            display.textContent = slider.value;
        });
    }

    // Инициализация слайдеров для российского отчёта
    updateSliderValue('rus_fuzzy_cutoff', 'rus_fuzzy_value');
    updateSliderValue('rus_token_overlap', 'rus_token_value');

    // Инициализация слайдеров для иностранного отчёта
    updateSliderValue('foreign_fuzzy_cutoff', 'foreign_fuzzy_value');
    updateSliderValue('foreign_token_overlap', 'foreign_token_value');

    // Функция для показа прогресса
    function showProgress(progressId) {
        const progressEl = document.getElementById(progressId);
        progressEl.style.display = 'block';

        const progressBar = progressEl.querySelector('.progress-bar');
        progressBar.style.width = '0%';

        // Анимация прогресс-бара
        let width = 0;
        const interval = setInterval(() => {
            width += 1;
            progressBar.style.width = width + '%';

            if (width >= 90) {
                clearInterval(interval);
            }
        }, 50);

        return interval;
    }

    // Функция для скрытия прогресса
    function hideProgress(progressId, interval) {
        if (interval) {
            clearInterval(interval);
        }

        const progressEl = document.getElementById(progressId);
        const progressBar = progressEl.querySelector('.progress-bar');
        progressBar.style.width = '100%';

        setTimeout(() => {
            progressEl.style.display = 'none';
            progressBar.style.width = '0%';
        }, 500);
    }

    // Функция для скачивания файла
    function downloadBlob(blob, filename) {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();

        // Cleanup
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
    }

    // Функция для отправки формы
    async function submitForm(formId, endpoint, progressId) {
        const form = document.getElementById(formId);
        const formData = new FormData(form);

        const progressInterval = showProgress(progressId);

        try {
            const response = await fetch(endpoint, {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
            }

            const blob = await response.blob();

            // Определяем имя файла из заголовка или используем дефолтное
            const contentDisposition = response.headers.get('Content-Disposition');
            let filename = 'report_ready.xlsx';

            if (contentDisposition) {
                const match = contentDisposition.match(/filename="?([^"]+)"?/);
                if (match) {
                    filename = match[1];
                }
            }

            downloadBlob(blob, filename);

            // Показываем уведомление об успехе
            alert('Файл успешно обработан и загружен!');

        } catch (error) {
            console.error('Ошибка:', error);
            alert(`Ошибка обработки: ${error.message}`);
        } finally {
            hideProgress(progressId, progressInterval);
        }
    }

    // Обработчик для российского отчёта
    document.getElementById('rusForm').addEventListener('submit', async function(e) {
        e.preventDefault();

        const scheduleFile = document.getElementById('rus_schedule').files[0];
        const reportFile = document.getElementById('rus_report').files[0];

        if (!scheduleFile || !reportFile) {
            alert('Пожалуйста, выберите оба файла (сетка и отчёт)');
            return;
        }

        // Проверка размера файлов (максимум 100MB на файл)
        const maxSize = 100 * 1024 * 1024; // 100MB
        if (scheduleFile.size > maxSize || reportFile.size > maxSize) {
            alert('Размер файла не должен превышать 100MB');
            return;
        }

        await submitForm('rusForm', '/api/process/rus', 'rus_progress');
    });

    // Обработчик для иностранного отчёта
    document.getElementById('foreignForm').addEventListener('submit', async function(e) {
        e.preventDefault();

        const scheduleFile = document.getElementById('foreign_schedule').files[0];
        const reportFile = document.getElementById('foreign_report').files[0];

        if (!scheduleFile || !reportFile) {
            alert('Пожалуйста, выберите оба файла (сетка и отчёт)');
            return;
        }

        // Проверка размера файлов (максимум 100MB на файл)
        const maxSize = 100 * 1024 * 1024; // 100MB
        if (scheduleFile.size > maxSize || reportFile.size > maxSize) {
            alert('Размер файла не должен превышать 100MB');
            return;
        }

        await submitForm('foreignForm', '/api/process/foreign', 'foreign_progress');
    });

    // Обработчики для drag & drop (опционально)
    function setupDragAndDrop(inputId) {
        const input = document.getElementById(inputId);
        const parent = input.closest('.file-group');

        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            parent.addEventListener(eventName, preventDefaults, false);
        });

        function preventDefaults(e) {
            e.preventDefault();
            e.stopPropagation();
        }

        ['dragenter', 'dragover'].forEach(eventName => {
            parent.addEventListener(eventName, highlight, false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            parent.addEventListener(eventName, unhighlight, false);
        });

        function highlight(e) {
            parent.classList.add('drag-over');
        }

        function unhighlight(e) {
            parent.classList.remove('drag-over');
        }

        parent.addEventListener('drop', handleDrop, false);

        function handleDrop(e) {
            const dt = e.dataTransfer;
            const files = dt.files;

            if (files.length > 0) {
                input.files = files;
                // Триггерим событие change для валидации
                input.dispatchEvent(new Event('change', { bubbles: true }));
            }
        }
    }

    // Настройка drag & drop для всех file input'ов
    setupDragAndDrop('rus_schedule');
    setupDragAndDrop('rus_report');
    setupDragAndDrop('foreign_schedule');
    setupDragAndDrop('foreign_report');

    // Валидация файлов при выборе
    document.querySelectorAll('input[type="file"]').forEach(input => {
        input.addEventListener('change', function() {
            const file = this.files[0];
            if (!file) return;

            // Проверка расширения
            const allowedExtensions = ['.xls', '.xlsx'];
            const fileName = file.name.toLowerCase();
            const isValidExtension = allowedExtensions.some(ext => fileName.endsWith(ext));

            if (!isValidExtension) {
                alert('Пожалуйста, выберите файл Excel (.xls или .xlsx)');
                this.value = '';
                return;
            }

            // Проверка размера
            const maxSize = 100 * 1024 * 1024; // 100MB
            if (file.size > maxSize) {
                alert('Размер файла не должен превышать 100MB');
                this.value = '';
                return;
            }
        });
    });
});

