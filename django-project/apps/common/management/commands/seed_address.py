from django.core.management.base import BaseCommand
from apps.common.models import Province, District

LAOS_DATA = {
    "Vientiane Capital": [
        "Chanthabuly", "Sikhottabong", "Xaysetha", "Sisattanak",
        "Naxaithong", "Xaythany", "Hadxayfong", "Sangthong", "Mayparkngum"
    ],
    "Phongsaly": [
        "Phongsaly", "May", "Khoua", "Samphanh", "Boun Neua", "Yot Ou", "Boun Tay"
    ],
    "Luangnamtha": [
        "Namtha", "Sing", "Long", "Viengphoukha", "Nalae"
    ],
    "Oudomxay": [
        "Xay", "La", "Na Mo", "Nga", "Beng", "Houne", "Pakbeng"
    ],
    "Borkeo": [
        "Houayxay", "Ton Pheung", "Meung", "Pha Oudom", "Paktha"
    ],
    "Luangprabang": [
        "Luang Prabang", "Xiengngeun", "Nane", "Pak Ou", "Nam Bak",
        "Ngoi", "Pakxeng", "Phonxay", "Chomphet", "Viengkham", "Phoukhoune", "Phonthong"
    ],
    "Houaphan": [
        "Xam Neua", "Xiengkho", "Hiam", "Viengxay", "Houameuang",
        "Xamtay", "Sop Bao", "Et", "Kone", "Xon"
    ],
    "Xayaburi": [
        "Xayabury", "Khop", "Hongsa", "Ngeun", "Xienghone",
        "Phiang", "Parklai", "Kenethao", "Botene", "Thongmyxay", "Xaisathan"
    ],
    "Xiangkhouang": [
        "Pek", "Kham", "Nong Het", "Khoune", "Mok May", "Phou Kout", "Phaxay"
    ],
    "Vientiane Province": [
        "Phonhong", "Thoulakhom", "Keo Oudom", "Kasy", "Vangvieng",
        "Feuang", "Xanakharm", "Mad", "Hinhurp", "Viengkham", "Meun"
    ],
    "Borlikhamxai": [
        "Pakxan", "Thaphabath", "Pakkading", "Borikhanh", "Khamkeut", "Viengthong", "Xaichamphon"
    ],
    "Khammouan": [
        "Thakhek", "Mahaxay", "Nong Bok", "H Hinboun", "Nhommalath",
        "Boulapha", "Nakai", "Xebangfay", "Xaibouathong", "Kounkham"
    ],
    "Savannakhet": [
        "Kaysone Phomvihane", "Outhoumphone", "Atsaphangthong", "Phine", "Seponh",
        "Nong", "Thapangthong", "Songkhone", "Champhone", "Xonnabouly",
        "Xayboury", "Vilaboury", "Atsaphone", "Xayphouthong", "Thaphalanxay"
    ],
    "Salavan": [
        "Salavan", "Ta Oy", "Toumlane", "Lakhonepheng", "Vapy",
        "Khongsedone", "Lao Ngam", "Sa Mouay"
    ],
    "Sekong": [
        "La Mam", "Kaleum", "Dak Cheung", "Tha Teng"
    ],
    "Champasak": [
        "Pakse", "Sanasomboun", "Batiengchaleunsouk", "Paksong", "Pathouphone",
        "Phonthong", "Champassack", "Soukhoumma", "Mounlapamok", "Khong"
    ],
    "Attapeu": [
        "Xaysetha", "Samakkhixay", "Sanamxay", "Sanxay", "Phouvong"
    ],
    "Xaisomboun": [
        "Anouvong", "Thathom", "Longchaeng", "Hom", "Longxan"
    ]
}

class Command(BaseCommand):
    help = "Initial address data (province and district)"

    def handle(self, *args, **kwargs):
        province_count = 0
        district_count = 0

        for province_name, districts in LAOS_DATA.items():
            province, created = Province.objects.get_or_create(name=province_name)
            if created:
                province_count += 1

            for district_name in districts:
                _, d_created = District.objects.get_or_create(
                    province=province,
                    name=district_name
                )
                if d_created:
                    district_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Added provinces: {province_count} and districts: {district_count} successfully"
            )
        )
