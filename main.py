import flet as ft
import requests, base64, time, os

def main(page: ft.Page):
    page.title = "Insta Pro"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0
    page.window_width = 400
    page.window_height = 750
    cs = page.client_storage

    # உங்கள் நேரடி Firebase ஆன்லைன் சர்வர் இணைப்பு
    FB_URL = "https://firebaseio.com"

    SONGS = {
        "No Music": "",
        "Melody 🎵": "https://soundhelix.com",
        "Chill 🎧": "https://soundhelix.com"
    }
    REELS = [
        {"id": 1, "cat": "Nature", "u": "@nature_lover", "t": "மலைகளின் அழகு 🏔️ #nature", "lk": 140},
        {"id": 2, "cat": "Travel", "u": "@world_tour", "t": "காடுகளின் அமைதி 🌲 #travel", "lk": 210},
        {"id": 3, "cat": "Fun", "u": "@fun_zone", "t": "சிரிப்பு நேரம் 😂 #comedy", "lk": 320}
    ]

    if not cs.contains_key("saved_accs"):
        cs.set("saved_accs", {})
    if not cs.contains_key("act"):
        cs.set("act", "")
    if not cs.contains_key("blk"):
        cs.set("blk", [])

    # Firebase Cloud Functions
    def fb_get(p):
        try:
            r = requests.get(f"{FB_URL}/{p}.json", timeout=6)
            return r.json() if r.status_code == 200 else None
        except:
            return None

    def fb_post(p, d):
        try:
            requests.post(f"{FB_URL}/{p}.json", json=d, timeout=6)
        except:
            pass

    def fb_put(p, d):
        try:
            requests.put(f"{FB_URL}/{p}.json", json=d, timeout=6)
        except:
            pass

    def get_p():
        accs = cs.get("saved_accs") or {}
        act = cs.get("act")
        if act and act in accs:
            return accs[act]
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
        except:
            pass
        return ""

    # FilePicker & Audio Setup
    sel = {"p": "", "mode": ""}
    plbl = ft.Text("படம் தேர்ந்தெடுக்கப்படவில்லை", size=12)

    def on_file_res(e: ft.FilePickerResultEvent):
        if e.files:
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
    aud = ft.Audio(src=SONGS["Melody 🎵"], autoplay=False)
    page.overlay.append(aud)

    def avt(dp, b64, nm, r=20):
        img_str = b64 or dp
        if img_str and not img_str.startswith("http"):
            return ft.CircleAvatar(content=ft.Image(src_base64=img_str, fit=ft.ImageFit.COVER, width=r*2, height=r*2), radius=r)
        if img_str and img_str.startswith("http"):
            return ft.CircleAvatar(foreground_image_src=img_str, radius=r)
        return ft.CircleAvatar(content=ft.Text((nm[:2] if nm else "IP").upper(), weight=ft.FontWeight.BOLD), radius=r, bgcolor=ft.Colors.PINK_100)

    def dlg(t, c, act=None):
        d = ft.AlertDialog(title=ft.Text(t, weight=ft.FontWeight.BOLD), content=c, actions=act or [ft.TextButton("மூடு", on_click=lambda e: cls(d))])
        page.dialog = d
        d.open = True
        page.update()
        return d

    def cls(d):
        d.open = False
        page.update()

    def notify_user(msg):
        page.snack_bar = ft.SnackBar(ft.Text(msg), open=True)
        page.update()

    # =========================================================
    # 1. STRICT PASSWORD LOGIN & SIGN UP SCREEN
    # =========================================================
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
                err_txt.value = "⚠️ அதிகபட்சம் 4 ஐடிகள் மட்டுமே சேமிக்க முடியும்! ஒன்றை Logout செய்யவும்."
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

    # =========================================================
    # 2. MULTI-ACCOUNT SWITCHER (3–4 ஐடிகள் மாற்றும் வசதி)
    # =========================================================
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
                cs.set("act", list(accs.keys())[0])
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
            lst.append(ft.ElevatedButton("➕ Add Another Account (Password Login)", icon=ft.Icons.PERSON_ADD, on_click=lambda e: (cls(d), show_auth_screen(False))))
if uid not in blk and (time.time() - nd.get("time", 0) < 86400):
n_items.append(ft.Container(content=ft.Text(f"💭 {uid}: {nd.get('txt', '')}", size=12), bgcolor=ft.Colors.PURPLE_50, padding=8, border_radius=12))
ps_data = fb_get("posts") or {}
fd = ft.Column(spacing=15)
if not ps_data:
fd.controls.append(ft.Container(content=ft.Text("இன்னும் போஸ்ட்கள் இல்லை. கீழே '+' அழுத்தி பதிவிடுங்கள்!", text_align=ft.TextAlign.CENTER), padding=30))
else:
for pid, p in reversed(list(ps_data.items())):
if p.get("uname") not in blk:
fd.controls.append(p_card(pid, p))
return ft.Column([ft.Container(content=sr, padding=8), ft.Container(content=ft.Row(n_items, scroll=ft.ScrollMode.HIDDEN), padding=ft.padding.symmetric(horizontal=8)), ft.Divider(height=10), fd], scroll=ft.ScrollMode.AUTO)
def play_st(un, s):
if s.get("url"): aud.src, aud.autoplay = s["url"], True; aud.update()
img_w = ft.Image(src_base64=s["b64"], width=270, height=290, fit=ft.ImageFit.COVER) if s.get("b64") else ft.Image(src="picsum.photos", width=270, height=290)
d = dlg(f"{un} • 🎵 {s.get('song', '')}", img_w, [ft.ElevatedButton("மூடு", on_click=lambda e: (aud.pause(), cls(d)))])
def add_st():
sel["p"], sel["mode"], plbl.value = "", "story", "படம் இல்லை"
dd = ft.Dropdown(label="பாடல்", options=[ft.dropdown.Option(k) for k in SONGS], value="Melody 🎵")
def sv(e):
fb_put(f"stories/{get_p()['uname']}", {"b64": img_to_b64(sel["p"]), "song": dd.value, "url": SONGS[dd.value], "time": time.time()})
cls(d); body.content = home_v(); page.update()
d = dlg("புதிய ஸ்டோரி", ft.Column([ft.ElevatedButton("கேலரி போட்டோ", on_click=lambda _: fp.pick_files(file_type=ft.FilePickerFileType.IMAGE)), plbl, dd], tight=True), [ft.ElevatedButton("பதிவிடு 🌍", on_click=sv)])
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
for pid, p in ps.items():
if kw in p.get("uname", "").lower() or kw in p.get("cap", "").lower():
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
def chat_v():
room = ft.TextField(label="Chat Room (group அல்லது Username)", value="group")
msg_list = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True, spacing=8)
msg_in = ft.TextField(hint_text="மெசேஜ் டைப் செய்யவும்...", expand=True)
def load_msgs(e=None):
msg_list.controls.clear()
cdata = fb_get(f"chats/{room.value.strip().lower() or 'group'}") or {}
me = get_p()["uname"]
for _, m in cdata.items():
is_me = (m.get("s") == me)
msg_list.controls.append(ft.Row([ft.Container(content=ft.Text(f"@{m.get('s')}: {m.get('t')}", color=ft.Colors.WHITE if is_me else ft.Colors.BLACK), bgcolor=ft.Colors.BLUE if is_me else ft.Colors.GREY_200, padding=10, border_radius=12)], alignment=ft.MainAxisAlignment.END if is_me else ft.MainAxisAlignment.START))
page.update()
def send_msg(e):
if msg_in.value.strip():
fb_post(f"chats/{room.value.strip().lower() or 'group'}", {"s": get_p()["uname"], "t": msg_in.value.strip(), "time": time.time()})
msg_in.value = ""; load_msgs()
load_msgs()
return ft.Container(content=ft.Column([ft.Row([room, ft.IconButton(ft.Icons.REFRESH, on_click=load_msgs)]), ft.Divider(), msg_list, ft.Row([msg_in, ft.IconButton(ft.Icons.SEND, on_click=send_msg, icon_color=ft.Colors.BLUE)])]), padding=10, expand=True)
def prof_v():
u = get_p()
ps = fb_get("posts") or {}
my_posts = [p for _, p in ps.items() if p.get("uname") == u["uname"]]
def edit_prof_and_pwd(e):
nk_in = ft.TextField(label="Nickname", value=u["nick"])
bio_in = ft.TextField(label="Bio", value=u["bio"])
old_p = ft.TextField(label="பழைய Password (மாற்ற வேண்டுமெனில்)", password=True)
new_p = ft.TextField(label="புதிய Password", password=True)
def save_ed(ev):
u["nick"], u["bio"] = nk_in.value, bio_in.value
if new_p.value.strip():
if old_p.value.strip() != str(u.get("pwd", "")):
notify_user("❌ பழைய Password தவறானது!")
return
u["pwd"] = new_p.value.strip()
save_p(u)
cls(d)
body.content = prof_v()
notify_user("✅ Profile & Password சேமிக்கப்பட்டது!")
page.update()
d = dlg("✏️ Edit Profile & Password", ft.Column([
ft.ElevatedButton("📷 DP மாற்று", on_click=lambda _: (sel.update({"mode": "dp"}), fp.pick_files(file_type=ft.FilePickerFileType.IMAGE))),
nk_in, bio_in, ft.Divider(), old_p, new_p
], tight=True), [ft.ElevatedButton("சேமி", on_click=save_ed)])
grid = ft.GridView(runs_count=3, spacing=4, run_spacing=4, expand=True)
for p in my_posts:
grid.controls.append(ft.Image(src_base64=p["b64"], fit=ft.ImageFit.COVER) if p.get("b64") else ft.Container(content=ft.Text(p.get("cap", "")[:15], size=11, color=ft.Colors.WHITE), bgcolor=ft.Colors.PINK_300, alignment=ft.alignment.center))
return ft.Container(content=ft.Column([
ft.Row([avt(u.get("dp", ""), "", u["uname"], 38), ft.Column([ft.Text(str(len(my_posts)), weight=ft.FontWeight.BOLD, size=16), ft.Text("Posts", size=12)], horizontal_alignment=ft.CrossAxisAlignment.CENTER), ft.Column([ft.Text(str(u["flw"]), weight=ft.FontWeight.BOLD, size=16), ft.Text("Followers", size=12)], horizontal_alignment=ft.CrossAxisAlignment.CENTER), ft.Column([ft.Text(str(u["flg"]), weight=ft.FontWeight.BOLD, size=16), ft.Text("Following", size=12)], horizontal_alignment=ft.CrossAxisAlignment.CENTER)], alignment=ft.MainAxisAlignment.SPACE_AROUND),
ft.Text(u["nick"], weight=ft.FontWeight.BOLD, size=15),
ft.Text(u["bio"], size=13),
ft.Row([
ft.ElevatedButton("Edit / Password", on_click=edit_prof_and_pwd, expand=True),
ft.ElevatedButton(f"Switch ({len(cs.get('saved_accs') or {})}/4)", on_click=lambda e: switch_acc(), expand=True)
]),
ft.Divider(), grid
]), padding=15, expand=True)
def show_notifs(e):
ndata = fb_get("notifications") or {}
me = get_p()["uname"]
items = [ft.Text(n.get("msg", ""), size=13) for _, n in reversed(list(ndata.items())) if n.get("to") == me]
if not items:
items.append(ft.Text("புதிய அறிவிப்புகள் இல்லை.", color=ft.Colors.GREY))
dlg("❤️ Notifications", ft.Column(items[:15], scroll=ft.ScrollMode.AUTO, height=250, tight=True))
def load_main_app():
page.controls.clear()
u = get_p()
top_u = ft.TextButton(f"@{u['uname']} ▼", on_click=lambda e: switch_acc())
page.appbar = ft.AppBar(
title=ft.Row([ft.Text("Insta Pro", weight=ft.FontWeight.BOLD, size=20, color=ft.Colors.PINK), top_u]),
bgcolor=ft.Colors.WHITE,
actions=[
ft.IconButton(ft.Icons.FAVORITE_BORDER, on_click=show_notifs),
ft.IconButton(ft.Icons.CHAT_OUTLINED, on_click=lambda e: (setattr(body, "content", chat_v()), page.update()))
]
)
def on_nav(e):
idx = e.control.selected_index
if idx == 0: body.content = home_v()
elif idx == 1: body.content = search_v()
elif idx == 2: body.content = create_v()
elif idx == 3: body.content = reels_v()
elif idx == 4: body.content = prof_v()
page.update()
nav_bar = ft.NavigationBar(
selected_index=0, on_change=on_nav,
destinations=[
ft.NavigationBarDestination(icon=ft.Icons.HOME_OUTLINED, selected_icon=ft.Icons.HOME, label="Home"),
ft.NavigationBarDestination(icon=ft.Icons.SEARCH, label="Search"),
ft.NavigationBarDestination(icon=ft.Icons.ADD_BOX_OUTLINED, selected_icon=ft.Icons.ADD_BOX, label="Post"),
ft.NavigationBarDestination(icon=ft.Icons.VIDEO_LIBRARY_OUTLINED, selected_icon=ft.Icons.VIDEO_LIBRARY, label="Reels"),
ft.NavigationBarDestination(icon=ft.Icons.PERSON_OUTLINE, selected_icon=ft.Icons.PERSON, label="Profile"),
]
)
body.content = home_v()
page.add(body, nav_bar)
page.update()
if get_p():
load_main_app()
else:
show_auth_screen(False)
ft.app(target=main)
