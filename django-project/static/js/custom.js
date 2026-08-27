// apps/quotation/static/js/custom.js 
function openNewCustomerModal() {
    document.getElementById("newCustomerModal").style.display = "block";
}
function closeNewCustomerModal() {
    document.getElementById("newCustomerModal").style.display = "none";
}
// Function READ CSRF token from cookie
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Submit new customer via AJAX
function submitNewCustomerForm() {
    const form = document.getElementById("new-customer-form");
    const formData = new FormData(form);
    const url = document.querySelector("#newCustomerModal footer button[data-url]").dataset.url;

    fetch(url, {
        method: "POST",
        headers: {
            "X-CSRFToken": getCookie('csrftoken') // ใช้ cookie ของ Django
        },
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const select = document.getElementById("id_customer_info");
            const option = document.createElement("option");
            option.value = data.customer.id;
            option.text = data.customer.name;
            option.selected = true;
            select.appendChild(option);
            select.dispatchEvent(new Event('change')); // สำหรับ select2

            closeNewCustomerModal();
            form.reset();
        } else {
            alert("ບໍ່ສາມາດບັນທຶກລູກຄ້າໄດ້:\n" + JSON.stringify(data.errors));
        }
    })
    .catch(err => {
        console.error(err);
        alert("ບໍ່ສາມາດບັນທຶກຂໍ້ມູນລູກຄ້າໄດ້.");
    });
}