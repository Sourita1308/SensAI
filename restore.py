import re

url_sign = "https://lh3.googleusercontent.com/aida/AP1WRLtU28KEnYY8lgh7DfLWAjgrqHiCdKWc191N6J6smydAPZQ_V_2_dXtSvdohhGxf8tUfyGqZA87ALQi75acxDcNmbGeQOnoXxuyP_tai3DYJP4YIJdFMbjlpF4u4h9Jze9JFYulB27XjGNEy3v2IHeouCAPRZOhZkX74Asr42ZAsK1EmtJRV9-YkW94eb470ArChm_tqPcNnJgYExyPmnvbawTpkY6m6RWR10H9ANj-2lV4ai8veSGyfQSc"
url_emo = "https://lh3.googleusercontent.com/aida/AP1WRLtwpc5Ze64_W__2rWfFiszmuNKgerosLP7FGCfj6PB_D06T2ZOvi4uD_ogsR_9OsEGV_C3OjmvH8UNmygMIaMclj02AIHxVSdXtR0g5P5sDCPCNfFHRWCKtggHdnG3XPCvgvFYxrMzIUWXIYR1vb951yWIzP1DHzUJUm3Yp_v86xZH6yAt0Uk4viTZiu2W3gM2oFZXiylPX2hlOc5-_1MhvkSWVeFM19aO3xRzsjqNaM6AsmmRUJUBdOns"
url_scene = "https://lh3.googleusercontent.com/aida/AP1WRLtWmOCClTnCwez_QnsOgY6U_xsT_Hg5DBCQ-du_4HEf7MdPFfm-d0sqdoVcBXpgWwjuNXtJbeFPiGKMWY2FKrY1lHyrrTV0sHMuvfHDgZU7PBD9fRbWsLaH3Zx2pZCthKCqV5TyPjFnXJ-Sk1YUNMz4Ok8Y3u-rvkETGTN2ddNI0sjgrTQl6NKIvX7rCxOHDtNykAcOpQPAIYqvESvPLQiQF8joZk09LDiFWwDJREfawUNRvpenUi0uzg"
url_nova = "https://lh3.googleusercontent.com/aida/AP1WRLvYun4SAvOme4MWZV6evMMwNwJ0YzzGKj-k8jCVx2rygQn0f5O5hB02ifLWidPFsfSH0G1DY7DIT26-cN6v0R5kXeGQpR2CYM8xLxOe46YFiDQDtdVyo0-4LIOlZ7ar5ZLUMT_BkppKQvAV21eMMxxlC1EwP6mda-0s-PPmdsJClJ_QsMe0VZrKK8EXrEICuQRtyCt24A_kJsQyXCipDvWVK4bKlnremftPbyZ3AX24YO0e6P71cFhCnBw"

with open('views/landing_page.py', 'r', encoding='utf-8') as f:
    lines = f.read().split('\n')

# We know lines:
# 452 (nova), 505 (img1), 507 (img3), 508 (img4), 1091 (nova), 1156 (img3), 1164 (img4), 1172 (img1)
# Note: indexes are line_number - 1

def replace_b64(line_idx, new_url):
    line = lines[line_idx]
    lines[line_idx] = re.sub(r'data:image/jpeg;base64,[a-zA-Z0-9+/=]+', new_url, line)

replace_b64(451, url_nova)
replace_b64(1090, url_nova)
replace_b64(504, url_sign)
replace_b64(1171, url_sign)
replace_b64(506, url_emo)
replace_b64(1155, url_emo)
replace_b64(507, url_scene)
replace_b64(1163, url_scene)

with open('views/landing_page.py', 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))


# Fix _patch_navbar_hero.py
url_logo = "https://lh3.googleusercontent.com/aida/AP1WRLvMsY_1nR8NxOd0I154HrytjSEtXPYgZalDCXpLfyAyckWfBtD2i_ORlYCuTcpWAQib7s3bKUNJViEeGv2nlPI83rKzLCSzOOkATVNC9GtDIP_hiZOjaOnUgXG6O9eIdgadnIhB78d3n_mcEbTApDF1ewmMtOPv-bu5xEiCDp01jOKpkCCDIp8TLgmEtBCTNMVQdzidmPh_InKPnjkDqV56rXcFfVCU3AYf-nXTPjuUQV3emfQoEe"
url_bg = "https://lh3.googleusercontent.com/aida/AP1WRLtfRALLZchD_6xIGy89ab967jK91claOLMuPtvtKUyKqntMw1twJTDobZ2tB8NFr-0SoIuFGDt46FXpRMf0sMp6hpWf9RLxRYJijdIHbYymU9FR9JPDgcF9ODSJUfGfrwmmVdxRGcj95pdVvDnZj2rB8DE6gkGUBKqG6lJ2o8qJeJ0iW2B9W8S2vnwAT5uUAAZVBmymxyDHJKIC_I6C4ScNDH_87QYldknNI7HiFHdpU4thfouZPo"

with open('views/_patch_navbar_hero.py', 'r', encoding='utf-8') as f:
    ph_lines = f.read().split('\n')
ph_lines[13] = f'LOGO_URL = "{url_logo}"'
ph_lines[14] = f'BG_URL    = "{url_bg}"'
with open('views/_patch_navbar_hero.py', 'w', encoding='utf-8') as f:
    f.write('\n'.join(ph_lines))


# Fix nova_page.py
nova_bg = "https://lh3.googleusercontent.com/aida/AP1WRLvP-iGszTnj-sK8440-iIuV-hZ_Jt1iK7jV-lJ3wS3_Hn4YxGq9tT5yOQz9YjY8ZtV5wR_tYxS9P_M4"
with open('views/nova_page.py', 'r', encoding='utf-8') as f:
    nv_lines = f.read().split('\n')
nv_lines[523] = re.sub(r"data:image/jpeg;base64,[a-zA-Z0-9+/=]+", nova_bg, nv_lines[523])
with open('views/nova_page.py', 'w', encoding='utf-8') as f:
    f.write('\n'.join(nv_lines))

print("Restoration complete!")
