function initChainedAddress(scope = document) {
    const provinceSelects = scope.querySelectorAll('select[id$="_province"], select[id$="-province"]');

    provinceSelects.forEach(function (provinceSelect) {
        const districtId = provinceSelect.id.replace(/([_-])province$/, "$1district");
        const districtSelect = document.getElementById(districtId);

        if (!districtSelect) return;

        function updateDistricts(provinceId, selectedDistrictId = null) {
            districtSelect.innerHTML = '<option value="">---------</option>';
            if (!provinceId) return;

            fetch(`/common/ajax/load-districts/?province_id=${provinceId}`)
                .then(response => response.json())
                .then(data => {
                    data.forEach(district => {
                        const option = document.createElement("option");
                        option.value = district.id;
                        option.textContent = district.name;
                        if (selectedDistrictId && String(district.id) === String(selectedDistrictId)) {
                            option.selected = true;
                        }
                        districtSelect.appendChild(option);
                    });
                });
        }

        provinceSelect.addEventListener("change", function () {
            updateDistricts(this.value);
        });

        if (provinceSelect.value) {
            updateDistricts(provinceSelect.value, districtSelect.value);
        } else {
            districtSelect.innerHTML = '<option value="">---------</option>';
        }
    });
}

document.addEventListener("DOMContentLoaded", function () {
    initChainedAddress(document);

    document.addEventListener("formset:added", function (event) {
        initChainedAddress(event.target);
    });
});

