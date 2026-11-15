import flet as ft
import sqlite3
import os

def main(page: ft.Page):
    page.title = "KPR"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0
    OWNER_CODE = "1234"

    conn = sqlite3.connect("kpr.db", check_same_thread=False)
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS profile (id INTEGER PRIMARY KEY, uname TEXT, nick TEXT, bio TEXT, dp TEXT, note TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS posts (id INTEGER PRIMARY KEY AUTOINCREMENT, uname TEXT, img TEXT, cap TEXT, likes INTEGER)")
    c.execute("CREATE TABLE IF NOT EXISTS msgs (id INTEGER PRIMARY KEY AUTOINCREMENT, sender TEXT, txt TEXT)")
    conn.commit()

    c.execute("SELECT * FROM profile WHERE id=1")
    if not c.fetchone():
        c.execute("INSERT INTO profile VALUES (1, 'kpr_official', 'KPR 😎', 'எனது சொந்த KPR ஆப்! 🚀', '', 'புதிய தொடக்கம்! ✨')")
        conn.commit()

    def get_prof():
        c.execute("SELECT uname, nick, bio, dp, note FROM profile WHERE id=1")
        r = c.fetchone()
        return {"uname": r, "nick": r, "bio": r, "dp": r, "note": r}

    sel_img = {"path": ""}
    pick_lbl = ft.Text("புகைப்படம் தேர்ந்தெடுக்கப்படவில்லை", size=12, color=ft.Colors.GREY_600)

    def on_pick(e: ft.FilePickerResultEvent):
        if e.files:
            sel_img["path"] = e.files.path
            pick_lbl.value = f"தேர்வு: {e.files.name}"
            page.update()

    fp = ft.FilePicker(on_result=on_pick)
    page.overlay.append(fp)

    def avatar(dp, name, r=20):
        if dp and os.path.exists(dp):
            return ft.CircleAvatar(foreground_image_src=dp, radius=r)
        return ft.CircleAvatar(content=ft.Text(name[:2].upper()), radius=r, bgcolor=ft.Colors.BLUE_200)

    def load_app():
        page.controls.clear()
        page.scroll = None
        body = ft.Container(expand=True)

        def home_view():
            u = get_prof()
            stories = [{"u": "உங்கள் ஸ்டோரி", "s": u["note"]}, {"u": "நண்பர் 1", "s": "காலை வணக்கம்! ☀️"}, {"u": "நண்பர் 2", "s": "KPR ஆப் சூப்பர்! 🔥"}]
            s_row = ft.Row(scroll=ft.ScrollMode.HIDDEN, spacing=12)
            for st in stories:
                s_row.controls.append(ft.GestureDetector(
                    on_click=lambda e, x=st: show_dlg(x["u"], ft.Text(x["s"], size=16)),
                    content=ft.Column([
                        ft.Container(content=avatar(u["dp"] if st["u"] == "உங்கள் ஸ்டோரி" else "", st["u"], 26), padding=2, border=ft.border.all(2, ft.Colors.PINK), border_radius=35),
                        ft.Text(st["u"][:10], size=11)
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=3)
                ))

            note_box = ft.Container(
                content=ft.Row([ft.Text(f"📝 Note: {u['note']}", size=13, italic=True, expand=True), ft.IconButton(ft.Icons.EDIT_NOTE, on_click=lambda e: edit_note())]),
                bgcolor=ft.Colors.BLUE_50, padding=8, border_radius=10, margin=ft.margin.symmetric(horizontal=10)
            )

            c.execute("SELECT id, uname, img, cap, likes FROM posts ORDER BY id DESC")
            posts = c.fetchall()
            feed = ft.Column(spacing=15)
            if not posts:
                feed.controls.append(ft.Container(content=ft.Text("இன்னும் போஸ்ட்கள் இல்லை. மேலே '+' அழுத்தி பதிவிடுங்கள்!", text_align=ft.TextAlign.CENTER), padding=30))
            else:
                for p in posts:
                    feed.controls.append(post_card(p))
            return ft.Column([ft.Container(content=s_row, padding=10), note_box, ft.Divider(height=10), feed], scroll=ft.ScrollMode.AUTO)

        def post_card(p):
            pid, un, img, cap, likes = p
            l_lbl = ft.Text(f"{likes} likes", weight=ft.FontWeight.BOLD, size=13)
            def like_click(e):
                nonlocal likes
                likes += 1
                c.execute("UPDATE posts SET likes=? WHERE id=?", (likes, pid))
                conn.commit()
                l_btn.icon, l_btn.icon_color, l_lbl.value = ft.Icons.FAVORITE, ft.Colors.RED, f"{likes} likes"
                page.update()
            l_btn = ft.IconButton(ft.Icons.FAVORITE_BORDER, on_click=like_click)
            media = ft.Image(src=img, width=400, height=280, fit=ft.ImageFit.COVER, border_radius=8) if (img and os.path.exists(img)) else ft.Container(content=ft.Text(cap, size=18, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD), width=400, height=200, bgcolor=ft.Colors.INDIGO_400, alignment=ft.alignment.center, border_radius=8, padding=15)
            return ft.Container(content=ft.Column([ft.Row([avatar("", un, 16), ft.Text(un, weight=ft.FontWeight.BOLD)]), media, ft.Row([l_btn, ft.Icon(ft.Icons.CHAT_BUBBLE_OUTLINE)]), l_lbl, ft.Text(f"{un}: {cap}", size=13)], spacing=4), padding=10, bgcolor=ft.Colors.WHITE)
