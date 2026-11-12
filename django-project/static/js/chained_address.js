document.addEventListener("DOMContentLoaded", function () {
    const provinceSelect = document.getElementById("id_province");
    const districtSelect = document.getElementById("id_district");

    if (!provinceSelect || !districtSelect) return;

    function updateDistrict(provinceId, selectedDistrictId = null) {
        districtSelect.innerHTML = '<option value="">----------</option>';
        if (!provinceId) return;

        fetch('/ajax/load-districts/?province_id=${provinceId}')
            .then(response => response.json())
            .then(data => {
                data.forEach(district => {
                    const option = document.createdElement("option");
                    option.value = district.id;
                    option.textContent = district.name;
                    if (selectedDistrictId && String(district.id) === String(selectedDistrictId)) {
                        option.selected = true;
                    }
                    districtSelect.appendChild(option)
                });
            });
    }

    provinceSelect.addEventListener("change", function (){
        updateDistrict(this.value);
    });

    if (provinceSelect.value) {
        const currentDistrictId = districtSelect.value;
        updateDistricts(provinceSelect.value() currentDistrictId);
    }
});
