from django.core.management.base import BaseCommand
from django.utils.translation import gettext_lazy as _

from apps.common.models import Province, District

LAOS_DATA = {
    "Vientiane Capital": {
        "lo": "ນະຄອນຫຼວງວຽງຈັນ",
        "districts": [
            ("Chanthabuly", "ຈັນທະບູລີ"),
            ("Sikhottabong", "ສີໂຄດຕະບອງ"),
            ("Xaysetha", "ໄຊເສດຖາ"),
            ("Sisattanak", "ສີສັດຕະນາກ"),
            ("Naxaithong", "ນາຊາຍທອງ"),
            ("Xaythany", "ໄຊທານີ"),
            ("Hadxayfong", "ຫາດຊາຍຟອງ"),
            ("Sangthong", "ສັງທອງ"),
            ("Mayparkngum", "ໃໝ່ປາກງື່ມ"),
        ],
    },
    "Phongsaly": {
        "lo": "ຜົ້ງສາລີ",
        "districts": [
            ("Phongsaly", "ຜົ້ງສາລີ"),
            ("Mai", "ໃໝ່"),
            ("Khoua", "ຂວາ"),
            ("Samphanh", "ສຳພັນ"),
            ("Boun Neua", "ບຸນເໜືອ"),
            ("Yot Ou", "ຍອດອູ"),
            ("Boun Tai", "ບຸນໃຕ້"),
        ],
    },
    "Luangnamtha": {
        "lo": "ຫຼວງນ້ຳທາ",
        "districts": [
            ("Namtha", "ນ້ຳທາ"),
            ("Sing", "ສິງ"),
            ("Long", "ລອງ"),
            ("Viengphoukha", "ວຽງພູຄາ"),
            ("Nalae", "ນາແລ"),
        ],
    },
    "Oudomxay": {
        "lo": "ອຸດົມໄຊ",
        "districts": [
            ("Xay", "ໄຊ"),
            ("La", "ຫຼາ"),
            ("Na Mor", "ນາໝໍ້"),
            ("Nga", "ງາ"),
            ("Beng", "ແບ່ງ"),
            ("Houne", "ຮຸນ"),
            ("Pakbeng", "ປາກແບ່ງ"),
        ],
    },
    "Borkeo": {
        "lo": "ບໍ່ແກ້ວ",
        "districts": [
            ("Houayxay", "ຫ້ວຍຊາຍ"),
            ("Ton Pheung", "ຕົ້ນເຜິ້ງ"),
            ("Meung", "ເມິງ"),
            ("Pha Oudom", "ຜາອຸດົມ"),
            ("Paktha", "ປາກທາ"),
        ],
    },
    "Luangprabang": {
        "lo": "ຫຼວງພະບາງ",
        "districts": [
            ("Luang Prabang", "ຫຼວງພະບາງ"),
            ("Xiengngeun", "ຊຽງເງິນ"),
            ("Nane", "ນານ"),
            ("Pak Ou", "ປາກອູ"),
            ("Nam Bak", "ນ້ຳບາກ"),
            ("Ngoi", "ງອຍ"),
            ("Pakxeng", "ປາກແຊງ"),
            ("Phonxay", "ໂພນໄຊ"),
            ("Chomphet", "ຈອມເພັດ"),
            ("Viengkham", "ວຽງຄຳ"),
            ("Phoukhoune", "ພູຄູນ"),
            ("Phonthong", "ໂພນທອງ"),
        ],
    },
    "Houaphan": {
        "lo": "ຫົວພັນ",
        "districts": [
            ("Xam Neua", "ຊຳເໜືອ"),
            ("Xiengkho", "ຊຽງຄໍ້"),
            ("Hiam", "ຮ້ຽມ"),
            ("Viengxai", "ວຽງໄຊ"),
            ("Houameuang", "ຫົວເມືອງ"),
            ("Xamtai", "ຊຳໃຕ້"),
            ("Sop Bao", "ສົບເບົາ"),
            ("Et", "ແອດ"),
            ("Kone", "ກວັນ"),
            ("Xon", "ຊ່ອນ"),
        ],
    },
    "Xayaburi": {
        "lo": "ໄຊຍະບູລີ",
        "districts": [
            ("Xayabury", "ໄຊຍະບູລີ"),
            ("Khop", "ຄອບ"),
            ("Hongsa", "ຫົງສາ"),
            ("Ngeun", "ເງິນ"),
            ("Xienghone", "ຊຽງຮ່ອນ"),
            ("Phiang", "ພຽງ"),
            ("Parklay", "ປາກລາຍ"),
            ("Kenethao", "ແກ່ນທ້າວ"),
            ("Botene", "ບໍ່ແຕນ"),
            ("Thongmyxay", "ທົ່ງມີໄຊ"),
            ("Xaisathan", "ໄຊສະຖານ"),
        ],
    },
    "Xiangkhouang": {
        "lo": "ຊຽງຂວາງ",
        "districts": [
            ("Pek", "ແປກ"),
            ("Kham", "ຄຳ"),
            ("Nong Het", "ໜອງແຮດ"),
            ("Khoune", "ຄູນ"),
            ("Mok Mai", "ໝອກໃໝ່"),
            ("Phou Kout", "ພູກູດ"),
            ("Phaxai", "ຜາໄຊ"),
        ],
    },
    "Vientiane Province": {
        "lo": "ວຽງຈັນ",
        "districts": [
            ("Phonhong", "ໂພນໂຮງ"),
            ("Thoulakhom", "ທຸລະຄົມ"),
            ("Keo Oudom", "ແກ້ວອຸດົມ"),
            ("Kasy", "ກາສີ"),
            ("Vangvieng", "ວັງວຽງ"),
            ("Feuang", "ເຟືອງ"),
            ("Xanakharm", "ຊະນະຄາມ"),
            ("Mad", "ແມດ"),
            ("Hinhurp", "ຫີນເຫີບ"),
            ("Viengkham", "ວຽງຄຳ"),
            ("Meun", "ເມືອນ"),
        ],
    },
    "Borlikhamxai": {
        "lo": "ບໍລິຄຳໄຊ",
        "districts": [
            ("Pakxan", "ປາກຊັນ"),
            ("Thaphabath", "ທ່າພະບາດ"),
            ("Pakkading", "ປາກກະດິງ"),
            ("Borikhanh", "ບໍລິຄັນ"),
            ("Khamkeut", "ຄຳເກີດ"),
            ("Viengthong", "ວຽງທອງ"),
            ("Xaichamphon", "ໄຊຈຳພອນ"),
        ],
    },
    "Khammouan": {
        "lo": "ຄຳມ່ວນ",
        "districts": [
            ("Thakhek", "ທ່າແຂກ"),
            ("Mahaxay", "ມະຫາໄຊ"),
            ("Nong Bok", "ໜອງບົກ"),
            ("H Hinboun", "ຫີນບູນ"),
            ("Nhommalath", "ຍົມມະລາດ"),
            ("Boulapha", "ບົວລະພາ"),
            ("Nakai", "ນາກາຍ"),
            ("Xebangfay", "ເຊບັ້ງໄຟ"),
            ("Xaibouathong", "ໄຊບົວທອງ"),
            ("Kounkham", "ຄູນຄຳ"),
        ],
    },
    "Savannakhet": {
        "lo": "ສະຫວັນນະເຂດ",
        "districts": [
            ("Kaysone Phomvihane", "ໄກສອນ ພົມວິຫານ"),
            ("Outhoumphone", "ອຸທຸມພອນ"),
            ("Atsaphangthong", "ອາດສະພັງທອງ"),
            ("Phine", "ພີນ"),
            ("Seponh", "ເຊໂປນ"),
            ("Nong", "ໜອງ"),
            ("Thapangthong", "ທ່າປາງທອງ"),
            ("Songkhone", "ສອງຄອນ"),
            ("Champhone", "ຈຳພອນ"),
            ("Xonnabouly", "ຊົນນະບູລີ"),
            ("Xayboury", "ໄຊບູລີ"),
            ("Vilaboury", "ວິລະບູລີ"),
            ("Atsaphone", "ອາດສະພອນ"),
            ("Xayphouthong", "ໄຊພູທອງ"),
            ("Thaphalanxay", "ພະລານໄຊ"),
        ],
    },
    "Salavan": {
        "lo": "ສາລະວັນ",
        "districts": [
            ("Salavan", "ສາລະວັນ"),
            ("Ta Oy", "ຕະໂອ້ຍ"),
            ("Toumlane", "ຕຸ້ມລານ"),
            ("Lakhonepheng", "ລະຄອນເພັງ"),
            ("Vapy", "ວາປີ"),
            ("Khongsedone", "ຂົງເຊໂດນ"),
            ("Lao Ngam", "ເລົ່າງາມ"),
            ("Sa Mouay", "ສະມ້ວຍ"),
        ],
    },
    "Sekong": {
        "lo": "ເຊກອງ",
        "districts": [
            ("La Mam", "ລະມາມ"),
            ("Kaleum", "ກະເລີມ"),
            ("Dak Cheung", "ດັກຈຶງ"),
            ("Tha Teng", "ທ່າແຕງ"),
        ],
    },
    "Champasak": {
        "lo": "ຈຳປາສັກ",
        "districts": [
            ("Pakse", "ປາກເຊ"),
            ("Sanasomboun", "ຊະນະສົມບູນ"),
            ("Batiengchaleunsouk", "ບາຈຽງຈະເລີນສຸກ"),
            ("Paksong", "ປາກຊ່ອງ"),
            ("Pathouphone", "ປະທຸມພອນ"),
            ("Phonthong", "ໂພນທອງ"),
            ("Champassack", "ຈຳປາສັກ"),
            ("Soukhoumma", "ສຸຂຸມາ"),
            ("Mounlapamok", "ມູນລະປະໂມກ"),
            ("Khong", "ໂຂງ"),
        ],
    },
    "Attapeu": {
        "lo": "ອັດຕະປື",
        "districts": [
            ("Xaysetha", "ໄຊເສດຖາ"),
            ("Samakkhixay", "ສາມັກຄີໄຊ"),
            ("Sanamxay", "ສະໜາມໄຊ"),
            ("Sanxay", "ແສນໄຊ"),
            ("Phouvong", "ພູວົງ"),
        ],
    },
    "Xaisomboun": {
        "lo": "ໄຊສົມບູນ",
        "districts": [
            ("Anouvong", "ອະນຸວົງ"),
            ("Thathom", "ທ່າໂທມ"),
            ("Longchaeng", "ລ້ອງແຈ້ງ"),
            ("Hom", "ຮົ່ມ"),
            ("Longxan", "ລ້ອງຊານ"),
        ],
    },
}


class Command(BaseCommand):
    help = _("Initial address data (province and district)")

    def handle(self, *args, **kwargs):
        province_count = 0
        district_count = 0

        for province_name, info in LAOS_DATA.items():
            province, created = Province.objects.update_or_create(
                name=province_name,
                defaults={"name_lo": info["lo"]},
            )
            if created:
                province_count += 1

            for name_en, name_lo in info["districts"]:
                district, d_created = District.objects.update_or_create(
                    province=province,
                    name=name_en,
                    defaults={"name_lo": name_lo},
                )
                if d_created:
                    district_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                _("Added provinces: %(provinces)d and districts: %(districts)d successfully")
                % {"provinces": province_count, "districts": district_count}
            )
        )
