import flet as ft
import requests, base64, time, os

def main(page: ft.Page):
    page.title = "Insta Pro"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0
    cs = page.client_storage

    FB_URL = "https://firebaseio.com"

    REELS = [
        {"id": 1, "cat": "Nature", "u": "@nature_lover", "t": "மலைகளின் அழகு 🏔️ #nature", "lk": 140},
        {"id": 2, "cat": "Travel", "u": "@world_tour", "t": "காடுகளின் அமைதி 🌲 #travel", "lk": 210},
        {"id": 3, "cat": "Fun", "u": "@fun_zone", "t": "சிரிப்பு நேரம் 😂 #comedy", "lk": 320}
    ]

    try:
        if not cs.contains_key("saved_accs"):
            cs.set("saved_accs", {})
        if not cs.contains_key("act"):
            cs.set("act", "")
        if not cs.contains_key("blk"):
            cs.set("blk", [])
    except Exception:
        pass

    def fb_get(p):
        try:
            r = requests.get(f"{FB_URL}/{p}.json", timeout=6)
            return r.json() if r.status_code == 200 else None
        except Exception:
            return None

    def fb_post(p, d):
        try:
            requests.post(f"{FB_URL}/{p}.json", json=d, timeout=6)
        except Exception:
            pass

    def fb_put(p, d):
        try:
            requests.put(f"{FB_URL}/{p}.json", json=d, timeout=6)
        except Exception:
            pass

    def get_p():
        try:
            accs = cs.get("saved_accs") or {}
            act = cs.get("act") or ""
            if act and act in accs:
                return accs[act]
        except Exception:
            pass
        return None

    def save_p(u):
        accs = cs.get("saved_accs") or {}
        uname = u["uname"]
        accs[uname] = u
        cs.set("saved_accs", accs)
        cs.set("act", uname)
        fb_put(f"users/{uname}", u)

    def img_to_b64(path):
        try:
            if path and os.path.exists(path):
                with open(path, "rb") as f:
                    return base64.b64encode(f.read()).decode("utf-8")
        except Exception:
            pass
        return ""

    sel = {"p": "", "mode": ""}
    plbl = ft.Text("படம் தேர்ந்தெடுக்கப்படவில்லை", size=12)

    def on_file_res(e: ft.FilePickerResultEvent):
        if e.files and len(e.files) > 0:
            sel["p"] = e.files[0].path
            plbl.value = f"✅ {e.files[0].name}"
            if sel["mode"] == "dp":
                u = get_p()
                if u:
                    u["dp"] = img_to_b64(sel["p"])
                    save_p(u)
                    load_main_app()
            page.update()

    fp = ft.FilePicker(on_result=on_file_res)
    page.overlay.append(fp)

    def avt(dp, b64, nm, r=20):
        img_str = b64 or dp
        try:
            if img_str and not img_str.startswith("http"):
                return ft.CircleAvatar(content=ft.Image(src_base64=img_str, fit=ft.ImageFit.COVER, width=r*2, height=r*2), radius=r)
            if img_str and img_str.startswith("http"):
                return ft.CircleAvatar(foreground_image_src=img_str, radius=r)
        except Exception:
            pass
        return ft.CircleAvatar(content=ft.Text((nm[:2] if nm else "IP").upper(), weight=ft.FontWeight.BOLD), radius=r, bgcolor=ft.Colors.PINK_100)

    def dlg(t, c, act=None):
        d = ft.AlertDialog(
            title=ft.Text(t, weight=ft.FontWeight.BOLD),
            content=c,
            actions=act or [ft.TextButton("மூடு", on_click=lambda e: cls(d))]
        )
        page.open(d)
        return d

    def cls(d):
        page.close(d)

    def notify_user(msg):
        page.open(ft.SnackBar(ft.Text(msg)))

    def show_auth_screen(is_signup=False):
        page.appbar = None
        page.controls.clear()

        u_in = ft.TextField(label="Username (உதா: ravi_01)", prefix_icon=ft.Icons.PERSON)
        p_in = ft.TextField(label="Password", password=True, can_reveal_password=True, prefix_icon=ft.Icons.LOCK)
        nk_in = ft.TextField(label="Nickname (உங்கள் பெயர்)", prefix_icon=ft.Icons.BADGE, visible=is_signup)
        bio_in = ft.TextField(label="Bio (உங்களைப் பற்றி)", prefix_icon=ft.Icons.INFO_OUTLINE, visible=is_signup)
        err_txt = ft.Text("", color=ft.Colors.RED, size=12)

        def handle_auth(e):
            uname = u_in.value.strip().lower().replace(" ", "_")
            pwd = p_in.value.strip()

            if not uname or not pwd:
                err_txt.value = "⚠️ Username மற்றும் Password இரண்டையும் கட்டாயம் உள்ளிடவும்!"
                page.update()
                return

            saved = cs.get("saved_accs") or {}
            if uname not in saved and len(saved) >= 4:
                err_txt.value = "⚠️ அதிகபட்சம் 4 ஐடிகள் மட்டுமே சேமிக்க முடியும்!"
                page.update()
                return

            user_data = fb_get(f"users/{uname}")

            if is_signup:
                if user_data:
                    err_txt.value = "❌ இந்த Username ஏற்கனவே உள்ளது. வேறு பெயர் தரவும்!"
                    page.update()
                    return
                if len(pwd) < 4:
                    err_txt.value = "⚠️ Password குறைந்தது 4 எழுத்துக்கள் இருக்க வேண்டும்!"
                    page.update()
                    return
                new_u = {
                    "uname": uname,
                    "pwd": pwd,
                    "nick": nk_in.value.strip() or uname,
                    "bio": bio_in.value.strip() or "Insta Pro User 🚀",
                    "dp": "",
                    "flw": 0,
                    "flg": 0
                }
                save_p(new_u)
                notify_user(f"🎉 வரவேற்கிறோம் @{uname}!")
                load_main_app()
            else:
                if not user_data:
                    err_txt.value = "❌ இந்த Username இல்லை. முதலில் Sign Up செய்யவும்!"
                    page.update()
                    return
                real_password = str(user_data.get("pwd", ""))
                if real_password == "" or real_password != pwd:
                    err_txt.value = "🔒 தவறான Password! அந்த ஐடியின் சரியான பாஸ்வேர்ட் தேவை."
                    page.update()
                    return
                save_p(user_data)
                notify_user(f"✅ @{uname} கணக்கில் லாகின் ஆகிவிட்டது!")
                load_main_app()

        saved = cs.get("saved_accs") or {}
        quick_logins = []
        if saved:
            quick_logins.append(ft.Text(f"சேமிக்கப்பட்ட கணக்குகள் ({len(saved)}/4):", size=12, color=ft.Colors.GREY))
            for k, v in saved.items():
                quick_logins.append(
                    ft.ListTile(
                        leading=avt(v.get("dp", ""), "", k, 18),
                        title=ft.Text(f"@{k}", weight=ft.FontWeight.BOLD),
                        trailing=ft.ElevatedButton("Open", on_click=lambda e, uk=k: (cs.set("act", uk), load_main_app()))
                    )
                )

        auth_card = ft.Container(
            content=ft.Column([
                ft.Icon(ft.Icons.CAMERA_ALT_ROUNDED, size=55, color=ft.Colors.PINK),
                ft.Text("Insta Pro", size=28, weight=ft.FontWeight.BOLD, color=ft.Colors.PINK),
                ft.Text("புதிய கணக்கு உருவாக்கவும்" if is_signup else "உங்கள் கணக்கில் லாகின் செய்யவும்", size=14, color=ft.Colors.GREY_700),
                u_in, p_in, nk_in, bio_in, err_txt,
                ft.ElevatedButton(
                    "Sign Up (பதிவு செய்)" if is_signup else "Log In (உள்நுழை)",
                    on_click=handle_auth,
                    bgcolor=ft.Colors.PINK, color=ft.Colors.WHITE, width=320, height=45
                ),
                ft.TextButton(
                    "ஏற்கனவே கணக்கு உள்ளதா? Log In" if is_signup else "புதிய கணக்கு வேண்டுமா? Sign Up",
                    on_click=lambda e: show_auth_screen(not is_signup)
                ),
                ft.Divider(),
                *quick_logins
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=12, scroll=ft.ScrollMode.AUTO),
            padding=25, expand=True
        )
        page.add(auth_card)
        page.update()

    def switch_acc():
        accs = cs.get("saved_accs") or {}
        act = cs.get("act")

        def sw(k):
            cs.set("act", k)
            cls(d)
            load_main_app()

        def logout_curr(e):
            if act in accs:
                del accs[act]
                cs.set("saved_accs", accs)
            cls(d)
            if accs:
                first_key = list(accs.keys())[0]
                cs.set("act", first_key)
                load_main_app()
            else:
                cs.set("act", "")
                show_auth_screen(False)

        lst = []
        for k, v in accs.items():
            lst.append(
                ft.ListTile(
                    leading=avt(v.get("dp", ""), "", k, 18),
                    title=ft.Text(f"@{k}", weight=ft.FontWeight.BOLD),
                    subtitle=ft.Text(v.get("nick", "")),
                    trailing=ft.Icon(ft.Icons.CHECK_CIRCLE, color=ft.Colors.GREEN) if k == act else ft.Text("Switch"),
                    on_click=lambda e, uk=k: sw(uk)
                )
            )
        lst.append(ft.Divider())
        if len(accs) < 4:
            lst.append(ft.ElevatedButton("➕ Add Another Account", icon=ft.Icons.PERSON_ADD, on_click=lambda e: (cls(d), show_auth_screen(False))))
        else:
            lst.append(ft.Text("⚠️ அதிகபட்சம் 4 ஐடிகள் சேமிக்கப்பட்டுள்ளன.", size=12, color=ft.Colors.ORANGE))
        lst.append(ft.TextButton("🚪 Logout Current Account", on_click=logout_curr, style=ft.ButtonStyle(color=ft.Colors.RED)))
        d = dlg(f"Switch Account ({len(accs)}/4)", ft.Column(lst, tight=True, scroll=ft.ScrollMode.AUTO))

    body = ft.Container(expand=True)

    def open_comments(pid, post_owner):
        c_list = ft.Column(scroll=ft.ScrollMode.AUTO, height=220, spacing=8)
        def load_c():
            c_list.controls.clear()
cdata = fb_get(f"posts/{pid}/comments") or {}
if not cdata or not isinstance(cdata, dict):
c_list.controls.append(ft.Text("இன்னும் கமெண்ட்கள் இல்லை.", size=12, color=ft.Colors.GREY))
else:
for _, cm in cdata.items():
if isinstance(cm, dict):
c_list.controls.append(ft.Container(content=ft.Text(f"💬 @{cm.get('u', 'user')}: {cm.get('txt', '')}", size=13), bgcolor=ft.Colors.GREY_100, padding=8, border_radius=8))
page.update()
c_input = ft.TextField(hint_text="கமெண்ட் எழுதுங்கள்...", expand=True, text_size=13)
def send_c(e):
if c_input.value.strip():
me = get_p()["uname"]
fb_post(f"posts/{pid}/comments", {"u": me, "txt": c_input.value.strip(), "time": time.time()})
fb_post("notifications", {"to": post_owner, "msg": f"💬 @{me} உங்கள் போஸ்டில் கமெண்ட் செய்தார்.", "time": time.time()})
c_input.value = ""
load_c()
load_c()
dlg("💬 கமெண்ட்கள்", ft.Column([c_list, ft.Row([c_input, ft.IconButton(ft.Icons.SEND, on_click=send_c)])], tight=True, width=300))
def share_item(title_txt):
to_user = ft.TextField(label="நண்பரின் Username (அல்லது group)", value="group")
def send_sh(e):
target = to_user.value.strip().lower() or "group"
fb_post(f"chats/{target}", {"s": get_p()["uname"], "t": title_txt, "time": time.time()})
cls(d)
notify_user(f"✅ '{target}' சாட்டிற்கு ஷேர் செய்யப்பட்டது!")
d = dlg("🚀 ஷேர் செய்", ft.Column([to_user], tight=True), [ft.ElevatedButton("அனுப்பு", on_click=send_sh)])
def home_v():
blk = cs.get("blk") or []
st_data = fb_get("stories") or {}
sr = ft.Row(scroll=ft.ScrollMode.HIDDEN, spacing=12)
sr.controls.append(ft.GestureDetector(
on_click=lambda e: add_st(),
content=ft.Column([ft.CircleAvatar(content=ft.Icon(ft.Icons.ADD, color=ft.Colors.WHITE), radius=25, bgcolor=ft.Colors.BLUE), ft.Text("Your Story", size=11)], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=3)
))
if isinstance(st_data, dict):
for uid, s in st_data.items():
if isinstance(s, dict) and uid not in blk and (time.time() - s.get("time", 0) < 86400):
sr.controls.append(ft.GestureDetector(
on_click=lambda e, x=s, un=uid: play_st(un, x),
content=ft.Column([ft.Container(content=avt("", s.get("b64", ""), un, 24), padding=2, border=ft.border.all(2, ft.Colors.PINK), border_radius=35), ft.Text(un[:10], size=11)], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=3)
))
nt_data = fb_get("notes") or {}
n_items = [ft.ElevatedButton("+ Note 📝", on_click=lambda e: ed_note(), style=ft.ButtonStyle(padding=5))]
if isinstance(nt_data, dict):
for uid, nd in nt_data.items():
if isinstance(nd, dict) and uid not in blk and (time.time() - nd.get("time", 0) < 86400):
n_items.append(ft.Container(content=ft.Text(f"💭 {uid}: {nd.get('txt', '')}", size=12), bgcolor=ft.Colors.PURPLE_50, padding=8, border_radius=12))
ps_data = fb_get("posts") or {}
fd = ft.Column(spacing=15)
if not ps_data or not isinstance(ps_data, dict):
fd.controls.append(ft.Container(content=ft.Text("இன்னும் போஸ்ட்கள் இல்லை. கீழே 'Post' அழுத்தி பதிவிடுங்கள்!", text_align=ft.TextAlign.CENTER), padding=30))
else:
for pid, p in reversed(list(ps_data.items())):
if isinstance(p, dict) and p.get("uname") not in blk:
fd.controls.append(p_card(pid, p))
return ft.Column([ft.Container(content=sr, padding=8), ft.Container(content=ft.Row(n_items, scroll=ft.ScrollMode.HIDDEN), padding=ft.padding.symmetric(horizontal=8)), ft.Divider(height=10), fd], scroll=ft.ScrollMode.AUTO)
def play_st(un, s):
img_w = ft.Image(src_base64=s["b64"], width=270, height=290, fit=ft.ImageFit.COVER) if s.get("b64") else ft.Container(content=ft.Text(f"📸 {un}'s Story", size=20, color=ft.Colors.WHITE), width=270, height=290, bgcolor=ft.Colors.PINK_300, alignment=ft.alignment.center)
d = dlg(f"{un} • Story", img_w, [ft.ElevatedButton("மூடு", on_click=lambda e: cls(d))])
def add_st():
sel["p"], sel["mode"], plbl.value = "", "story", "படம் இல்லை"
def sv(e):
fb_put(f"stories/{get_p()['uname']}", {"b64": img_to_b64(sel["p"]), "time": time.time()})
cls(d); body.content = home_v(); page.update()
d = dlg("புதிய ஸ்டோரி", ft.Column([ft.ElevatedButton("கேலரி போட்டோ", on_click=lambda _: fp.pick_files(file_type=ft.FilePickerFileType.IMAGE)), plbl], tight=True), [ft.ElevatedButton("பதிவிடு 🌍", on_click=sv)])
def ed_note():
nt_in = ft.TextField(label="உங்கள் 24h Note", max_length=60)
def sv_n(e):
if nt_in.value.strip():
fb_put(f"notes/{get_p()['uname']}", {"txt": nt_in.value.strip(), "time": time.time()})
cls(d); body.content = home_v(); page.update()
d = dlg("📝 24 மணி நேர Note", nt_in, [ft.ElevatedButton("பதிவிடு", on_click=sv_n)])
def p_card(pid, p):
lks = p.get("likes", 0)
c_count = len(p.get("comments", {})) if isinstance(p.get("comments"), dict) else 0
ll = ft.Text(f"{lks} likes • {c_count} comments", weight=ft.FontWeight.BOLD, size=13)
un, cap, b64 = p.get("uname", "u"), p.get("cap", ""), p.get("b64", "")
def lk(e):
nl = (fb_get(f"posts/{pid}/likes") or lks) + 1
fb_put(f"posts/{pid}/likes", nl)
fb_post("notifications", {"to": un, "msg": f"❤️ @{get_p()['uname']} உங்கள் போஸ்டை லைக் செய்தார்.", "time": time.time()})
lb.icon, lb.icon_color = ft.Icons.FAVORITE, ft.Colors.RED
ll.value = f"{nl} likes • {c_count} comments"
page.update()
def bk(e):
b = cs.get("blk") or []
if un not in b and un != get_p()["uname"]:
b.append(un); cs.set("blk", b); body.content = home_v(); page.update()
lb = ft.IconButton(ft.Icons.FAVORITE_BORDER, on_click=lk)
cb = ft.IconButton(ft.Icons.CHAT_BUBBLE_OUTLINE, on_click=lambda e: open_comments(pid, un))
sb = ft.IconButton(ft.Icons.SEND_OUTLINED, on_click=lambda e: share_item(f"📸 Post by @{un}: {cap}"))
med = ft.Image(src_base64=b64, width=400, height=260, fit=ft.ImageFit.COVER) if b64 else ft.Container(content=ft.Text(cap, size=18, color=ft.Colors.WHITE, text_align=ft.TextAlign.CENTER), width=400, height=180, bgcolor=ft.Colors.PINK_400, alignment=ft.alignment.center, padding=15)
return ft.Container(content=ft.Column([
ft.Row([ft.Row([avt("", "", un, 16), ft.Text(un, weight=ft.FontWeight.BOLD)]), ft.PopupMenuButton(items=[ft.PopupMenuItem(text="🚫 Block User", on_click=bk)])], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
med, ft.Row([lb, cb, sb], spacing=0), ll, ft.Text(f"{un}: {cap}", size=13)
], spacing=4), padding=10, bgcolor=ft.Colors.WHITE)
def search_v():
q_in = ft.TextField(hint_text="🔍 பயனர் பெயர் அல்லது போஸ்ட் தேடுங்கள்...", prefix_icon=ft.Icons.SEARCH)
res_col = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO, expand=True)
def do_search(e):
res_col.controls.clear()
kw = q_in.value.strip().lower()
ps = fb_get("posts") or {}
if isinstance(ps, dict):
for pid, p in ps.items():
if isinstance(p, dict) and (kw in p.get("uname", "").lower() or kw in p.get("cap", "").lower()):
res_col.controls.append(ft.ListTile(leading=avt("", p.get("b64", ""), p.get("uname", "U"), 20), title=ft.Text(f"@{p.get('uname')}"), subtitle=ft.Text(p.get("cap", "")[:40])))
if not res_col.controls:
res_col.controls.append(ft.Text("முடிவுகள் எதுவும் கிடைக்கவில்லை.", color=ft.Colors.GREY))
page.update()
q_in.on_change = do_search
do_search(None)
return ft.Container(content=ft.Column([q_in, res_col]), padding=12)
def create_v():
sel["p"], sel["mode"], plbl.value = "", "post", "படம் தேர்ந்தெடுக்கப்படவில்லை"
cap_in = ft.TextField(label="கேப்ஷன் எழுதுங்கள்...", multiline=True, min_lines=3)
def publish_post(e):
b64 = img_to_b64(sel["p"])
if not b64 and not cap_in.value.strip():
notify_user("⚠️ படம் அல்லது வாசகம் உள்ளிடவும்!"); return
fb_post("posts", {"uname": get_p()["uname"], "cap": cap_in.value.strip(), "b64": b64, "likes": 0, "time": time.time()})
notify_user("🎉 போஸ்ட் பதிவிடப்பட்டது!")
body.content = home_v(); page.update()
return ft.Container(content=ft.Column([ft.Text("புதிய போஸ்ட்", size=20, weight=ft.FontWeight.BOLD), ft.ElevatedButton("🖼️ கேலரி படம் எடு", on_click=lambda _: fp.pick_files(file_type=ft.FilePickerFileType.IMAGE)), plbl, cap_in, ft.ElevatedButton("பதிவிடு 🌍", on_click=publish_post, bgcolor=ft.Colors.BLUE, color=ft.Colors.WHITE, width=350)], spacing=15), padding=20)
def reels_v():
r_col = ft.Column(spacing=15, scroll=ft.ScrollMode.AUTO)
for r in REELS:
lk_txt = ft.Text(f"{r['lk']} likes", color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD)
def like_r(e, item=r, lbl=lk_txt):
item["lk"] += 1; lbl.value = f"{item['lk']} likes"; page.update()
r_col.controls.append(ft.Container(content=ft.Column([
ft.Row([ft.Text(r["u"], color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD), ft.Chip(label=ft.Text(r["cat"]))], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
ft.Container(content=ft.Column([ft.Icon(ft.Icons.PLAY_CIRCLE_FILL, size=60, color=ft.Colors.WHITE), ft.Text(r["t"], color=ft.Colors.WHITE, size=16, weight=ft.FontWeight.BOLD)], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER), height=250, bgcolor=ft.Colors.BLACK87, border_radius=12, alignment=ft.alignment.center),
ft.Row([ft.IconButton(ft.Icons.FAVORITE, icon_color=ft.Colors.RED, on_click=like_r), lk_txt, ft.IconButton(ft.Icons.SEND, icon_color=ft.Colors.WHITE, on_click=lambda e, x=r: share_item(f"🎬 Reel by {x['u']}: {x['t']}"))])
]), padding=12, bgcolor=ft.Colors.GREY_900, border_radius=15))
return ft.Container(content=r_col, padding=10)
