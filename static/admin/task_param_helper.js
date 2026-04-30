document.addEventListener("DOMContentLoaded", function () {

    const textarea = document.getElementById("id_task_template");

    if (!textarea) return;

    function insertAtCursor(text) {
        const start = textarea.selectionStart;
        const end = textarea.selectionEnd;

        textarea.value =
            textarea.value.substring(0, start) +
            text +
            textarea.value.substring(end);

        textarea.focus();
        textarea.selectionStart = textarea.selectionEnd = start + text.length;
    }

    let pointIndex = 0;
    const pointNames = ["A", "P", "Q", "B", "C", "D", "M", "N"];

    function addButton(label, callback) {
        const btn = document.createElement("button");
        btn.type = "button";
        btn.innerText = label;
        btn.style.marginRight = "5px";
        btn.style.marginBottom = "5px";

        btn.onclick = callback;

        textarea.parentNode.insertBefore(btn, textarea);
    }

    // кнопка число
    addButton("+ Число", function () {
        insertAtCursor("{a}");
    });

    // кнопка точка
    addButton("+ Точка", function () {
        const name = pointNames[pointIndex % pointNames.length];
        pointIndex++;
        insertAtCursor("{" + name + "}");
    });

    // кнопка прямая
    addButton("+ Прямая", function () {
        insertAtCursor("{line}");
    });

});