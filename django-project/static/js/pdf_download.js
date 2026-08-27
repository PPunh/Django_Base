/*
 * PDF download buttons/links (class "js-pdf-download").
 * Fetches the PDF, shows a spinner on the trigger while generating,
 * then saves the file using the filename from Content-Disposition.
 */
(function () {
    if (window.__pdfDownloadWired) return;
    window.__pdfDownloadWired = true;

    function pickFilename(disposition) {
        if (!disposition) return null;
        var match = disposition.match(/filename\*=UTF-8''([^;]+)/i);
        if (match) {
            try { return decodeURIComponent(match[1]); } catch (e) { /* fall through */ }
        }
        match = disposition.match(/filename="?([^";]+)"?/i);
        return match ? match[1] : null;
    }

    function setBusy(btn, busy) {
        var icon = btn.querySelector('i');
        var label = btn.querySelector('.js-pdf-label');
        btn.classList.toggle('w3-disabled', busy);
        if (busy) {
            btn.dataset.busy = '1';
            if (icon) {
                btn.dataset.iconClass = icon.className;
                icon.className = 'fa-solid fa-spinner fa-spin';
            }
            if (label) label.textContent = btn.dataset.generatingText || 'Generating...';
        } else {
            delete btn.dataset.busy;
            if (icon && btn.dataset.iconClass) icon.className = btn.dataset.iconClass;
            if (label) label.textContent = btn.dataset.label || 'Download PDF';
        }
    }

    document.addEventListener('click', function (e) {
        if (e.ctrlKey || e.metaKey || e.shiftKey || e.altKey) return;
        var btn = e.target.closest('a.js-pdf-download');
        if (!btn || btn.dataset.busy === '1') return;
        e.preventDefault();
        setBusy(btn, true);
        fetch(btn.href)
            .then(function (resp) {
                if (!resp.ok) throw new Error('HTTP ' + resp.status);
                return resp.blob().then(function (blob) {
                    return { blob: blob, name: pickFilename(resp.headers.get('Content-Disposition')) };
                });
            })
            .then(function (result) {
                var url = URL.createObjectURL(result.blob);
                var link = document.createElement('a');
                link.href = url;
                if (result.name) link.download = result.name;
                document.body.appendChild(link);
                link.click();
                link.remove();
                setTimeout(function () { URL.revokeObjectURL(url); }, 10000);
            })
            .catch(function () {
                alert(btn.dataset.errorText || 'Could not generate the PDF. Please try again.');
            })
            .finally(function () {
                setBusy(btn, false);
            });
    });
})();
