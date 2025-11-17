document.addEventListener('DOMContentLoaded', function() {

    // Описания для разных типов отчётов
    const descriptions = {
        rus: 'Обработка отчёта с колонкой "Наименование аудиовизуального произведения"',
        foreign: 'Обработка отчёта с колонкой "Название передачи"',
        third: 'Пока заглушка – файл возвращается без изменений'
    };

    // Динамическое изменение описания при выборе типа
    const reportTypeSelect = document.getElementById('report_type');
    const typeDescription = document.getElementById('type_description');

    reportTypeSelect.addEventListener('change', function() {
        typeDescription.textContent = descriptions[this.value] || '';
    });

    // Обновление значений слайдеров
    function updateSliderValue(sliderId, displayId) {
        const slider = document.getElementById(sliderId);
        const display = document.getElementById(displayId);

        slider.addEventListener('input', function() {
            display.textContent = slider.value;
        });
    }

    // Инициализация слайдеров
    updateSliderValue('fuzzy_cutoff', 'fuzzy_value');
    updateSliderValue('token_overlap', 'token_value');

    // Функция для показа прогресса
    function showProgress() {
        const progressEl = document.getElementById('progress');
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
    function hideProgress(interval) {
        if (interval) {
            clearInterval(interval);
        }

        const progressEl = document.getElementById('progress');
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

    // Обработчик для универсальной формы
    document.getElementById('unifiedForm').addEventListener('submit', async function(e) {
        e.preventDefault();

        const scheduleFile = document.getElementById('schedule_file').files[0];
        const reportFile = document.getElementById('report_file').files[0];
        const reportType = document.getElementById('report_type').value;

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

        // Определяем endpoint на основе типа отчёта
        const endpoint = `/api/process/${reportType}`;

        const formData = new FormData(this);
        const progressInterval = showProgress();

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
            let filename = `report_${reportType}_ready.xlsx`;

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
            hideProgress(progressInterval);
        }
    });

    // Обработчики для drag & drop
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

    // Настройка drag & drop для file input'ов
    setupDragAndDrop('schedule_file');
    setupDragAndDrop('report_file');

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

