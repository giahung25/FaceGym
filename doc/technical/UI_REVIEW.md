# Báo cáo Review UI — Gym Management System

**Ngày:** 2026-03-20 18:48
**Người review:** Claude Code (AI Assistant)
**Framework:** Flet (Python Desktop)
**Phạm vi:** Toàn bộ `gui/` — 5 màn hình + 2 components

---

## 1. Tổng quan cấu trúc UI

```
gui/
├── theme.py                  # Design tokens (màu, font, spacing, sizing)
├── dashboard.py              # Màn hình Dashboard
├── members.py                # Màn hình Hội viên
├── memberships.py            # Màn hình Gói tập & Đăng ký
├── equipment.py              # Màn hình Thiết bị
├── reports.py                # Màn hình Báo cáo
└── components/
    ├── sidebar.py            # Sidebar điều hướng
    └── header.py             # Header tìm kiếm + user info
```

**Layout pattern chung:** `ft.Row([Sidebar(220px), ft.Column([Header(64px), content])])`

---

## 2. Design System (`gui/theme.py`)

### Palette màu sắc
| Token | Giá trị | Dùng cho |
|-------|---------|---------|
| `ORANGE` | `#F97316` | Primary action, active state, highlight |
| `SIDEBAR_BG` | `#1C1C2E` | Nền sidebar (dark navy) |
| `BG` | `#F5F5F5` | Nền app |
| `CARD_BG` | `#FFFFFF` | Nền card/bảng |
| `GREEN` / `GREEN_LIGHT` | `#22C55E` / `#DCFCE7` | Trạng thái tốt/active |
| `AMBER` / `AMBER_LIGHT` | `#F59E0B` / `#FEF3C7` | Cảnh báo/sắp hết hạn |
| `RED` / `RED_LIGHT` | `#EF4444` / `#FEE2E2` | Nguy hiểm/hỏng |
| `BLUE` / `BLUE_LIGHT` | `#3B82F6` / `#DBEAFE` | Thông tin/mới |

**Nhận xét:** Palette đồng nhất, semantic color rõ ràng. Orange làm màu primary phù hợp với thương hiệu gym.

### Typography
| Token | Size | Ghi chú |
|-------|------|---------|
| `FONT_XS` | 11px | Caption, badge |
| `FONT_SM` | 12px | Body, table row |
| `FONT_MD` | 14px | Label, card title |
| `FONT_LG` | 16px | Section title |
| `FONT_XL` | 18px | Page subtitle |
| `FONT_2XL` | 22px | Page title |
| `FONT_3XL` | 28px | KPI số lớn |

**Nhận xét:** Scale typography hợp lý, có đủ cấp độ từ caption đến heading lớn.

### Spacing & Sizing
- `SIDEBAR_WIDTH = 220px` — cố định
- `HEADER_HEIGHT = 64px`
- `CARD_RADIUS = 12`, `BUTTON_RADIUS = 8`, `BADGE_RADIUS = 20`
- Padding scale: XS(4) → SM(8) → MD(12) → LG(16) → XL(20) → 2XL(24)

---

## 3. Components

### 3.1 Sidebar (`gui/components/sidebar.py`)

**Tính năng:**
- Logo section: Icon "G" + tên "GymAdmin" + subtitle "MANAGEMENT SYSTEM"
- 5 nav items: Dashboard, Members, Gym Packages, Equipment, Reports
- Active state: nền `ORANGE`, text/icon trắng
- Inactive: icon xám, text xám, hover ink effect
- Nút "Add Member" màu cam ở cuối sidebar

**Điểm tốt:**
- Icon + label rõ ràng
- Active highlight trực quan
- `ink=True` cho hiệu ứng ripple khi click
- Divider ngăn cách logo và nav

**Vấn đề / Đề xuất:**
- `equipment` icon dùng `SETTINGS_ROUNDED` — dễ nhầm với cài đặt hệ thống. Nên dùng `BUILD_ROUNDED` hoặc `FITNESS_CENTER`
- Nút "Add Member" bị cứng nhắc trong sidebar, không phù hợp khi đang ở màn hình Equipment/Reports
- Chưa có trạng thái hover rõ ràng cho inactive items (chỉ có ink, không có background hover)

---

### 3.2 Header (`gui/components/header.py`)

**Tính năng:**
- Search bar (width 320px) — placeholder "Search members, packages..."
- Notification button với badge cam (dot)
- User avatar + tên "Admin User" + role "Super Manager" + dropdown arrow

**Điểm tốt:**
- Layout `SPACE_BETWEEN` cân đối
- Border bottom phân tách header với content
- Notification badge trực quan

**Vấn đề / Đề xuất:**
- Search bar **hiện không có chức năng** (không có `on_change` handler) — chỉ là UI trang trí
- Notification button không có `on_click` handler
- User dropdown arrow không hoạt động
- Avatar chỉ hiện chữ "A" cứng — chưa lấy tên user thực

---

## 4. Màn hình Dashboard (`gui/dashboard.py`)

**Sections:**
1. **KPI Stats Row** — 4 stat cards: Tổng hội viên, Sắp hết hạn, Doanh thu tháng, Cần bảo trì
2. **Middle Row** — Recent Member Activity table + Revenue chart + Active Growth chart
3. **Gym Packages** — Package cards (dynamic từ DB)
4. **Equipment Status** — Equipment cards (dynamic từ DB, tối đa 4)
5. **Footer** — Version + năm

**Điểm tốt:**
- **Dữ liệu thực từ DB** — không còn mock data, đã kết nối services/repositories
- KPI cards có badge màu semantic (green/amber/red)
- Revenue chart tự custom bằng `ft.Column` + bar containers — sáng tạo
- Active Growth dùng `ft.ProgressBar` — trực quan
- Popular package có badge "POPULAR" + border cam nổi bật
- Equipment cards có wear level + progress bar theo status
- `scroll=ft.ScrollMode.AUTO` cho content area

**Vấn đề / Đề xuất:**
- Revenue chart dùng custom bar chart đơn giản — thanh cuối cùng luôn là màu cam (hardcode `i == len-1`), không phản ánh tháng hiện tại chính xác
- Equipment wear level cứng nhắc: `STATUS_WORKING → 0.25`, `STATUS_MAINTENANCE → 0.65`, `STATUS_BROKEN → 0.90` — không có dữ liệu wear thực
- "View All" và "Manage All" links không có `on_click` handler
- "View" button trong member row không có handler
- Footer hiện cứng `v1.0.0 • 2026`, nên lấy từ config
- Stat card badge_text_color không áp dụng nhất quán (parameter tồn tại nhưng một số card truyền sai)

---

## 5. Màn hình Members (`gui/members.py`)

**Tính năng:**
- Bảng hội viên: Avatar (initials + màu ngẫu nhiên) + Tên/SĐT + Email + Giới tính + Actions
- Tìm kiếm realtime theo tên/SĐT/email
- Dialog Thêm/Sửa với validation
- Dialog xác nhận xóa
- Stats text: Tổng / Active / Mới tháng này

**Điểm tốt:**
- Search `on_change` hoạt động realtime
- Dialog form đầy đủ fields
- Validation thông qua `member_svc.register_member()` — lỗi hiện trong dialog
- Confirm dialog trước khi xóa — tránh xóa nhầm
- Avatar color hash theo `m.id` — nhất quán giữa các lần render
- Lambda closure đúng: `lambda e, member=m: open_edit_dialog(member)`

**Vấn đề / Đề xuất:**
- Không có cột "Ngày tham gia" hay "Trạng thái subscription" trong bảng — thiếu thông tin quan trọng
- `f_dob` là TextField thủ công (YYYY-MM-DD) — nên dùng DatePicker nếu Flet hỗ trợ
- Không có pagination — khi nhiều hội viên sẽ render tất cả một lúc
- Missing `page.overlay` cleanup khi navigate — dialogs bị append mỗi lần vào màn hình

---

## 6. Màn hình Memberships (`gui/memberships.py`)

**Tính năng:**
- 2 tabs: "Gói tập" và "Đăng ký"
- Tab Gói tập: CRUD plans (tên, số ngày, giá, mô tả)
- Tab Đăng ký: Đăng ký hội viên vào gói, hiển thị danh sách subscriptions
- Auto-expire subscriptions khi refresh

**Điểm tốt:**
- Tab pattern tách biệt 2 concern rõ ràng
- `on_tab_change` refresh đúng tab đang xem
- Subscription row có đầy đủ: tên hội viên, gói, ngày bắt đầu, ngày kết thúc, trạng thái, giá
- Status color mapping (`active/expired/cancelled`) rõ ràng
- `auto_expire_subscriptions()` chạy tự động khi xem tab

**Vấn đề / Đề xuất:**
- `ft.Tabs` API đang dùng có thể không chuẩn — `ft.Tabs` + `ft.TabBar` + `ft.TabBarView` là cấu trúc không thông dụng trong Flet; thông thường chỉ cần `ft.Tabs(tabs=[ft.Tab(...)])`
- Tab "Đăng ký" không load data khi vào màn hình lần đầu (chỉ load "Gói tập") — cần gọi `refresh_subs()` cùng `refresh_plans()` hoặc lazy load khi switch tab
- Không có nút Cancel/Deactivate subscription
- `page.overlay.extend([...])` bị gọi mỗi lần navigate — overlay tích lũy

---

## 7. Màn hình Equipment (`gui/equipment.py`)

**Tính năng:**
- Bảng thiết bị: Tên, Loại, Số lượng, Trạng thái, Ngày mua, Actions
- Filter buttons: Tất cả / Hoạt động / Bảo trì / Hỏng
- Dialog Thêm/Sửa với đầy đủ fields
- Summary text: tổng theo trạng thái

**Điểm tốt:**
- Filter buttons đơn giản, hiệu quả
- Summary text cập nhật sau mỗi thao tác
- `STATUS_COLORS` mapping rõ ràng
- Lambda closure `item=eq` đúng cách

**Vấn đề / Đề xuất:**
- Filter buttons không cập nhật visual active state — không rõ filter nào đang được chọn
- Không có tìm kiếm theo tên thiết bị
- `getattr(eq, "location", "")` — field `location` có thể không có trong model, cần kiểm tra
- Không có sort column (theo tên, ngày mua, trạng thái)

---

## 8. Màn hình Reports (`gui/reports.py`)

**Tính năng:**
- 5 KPI cards: Tổng/Active/Mới hội viên + Doanh thu tháng/năm
- Equipment status summary (3 cột: Hoạt động/Bảo trì/Hỏng)
- Danh sách gói tập sắp hết hạn trong 7 ngày với countdown

**Điểm tốt:**
- `build_content()` + `refresh()` pattern sạch — rebuild toàn bộ khi cần
- Countdown badge đổi màu: đỏ (≤3 ngày), amber (>3 ngày) — rất trực quan
- Nút "Làm mới" cho phép reload data
- Hiển thị "Không có gói tập nào sắp hết hạn" khi empty

**Vấn đề / Đề xuất:**
- Không có biểu đồ revenue theo tháng (khác dashboard)
- KPI card thiếu icon — monotone so với dashboard
- Equipment section chỉ có 3 số — thiếu danh sách chi tiết thiết bị cần bảo trì
- Không có export/print chức năng (phù hợp với màn hình Reports)

---

## 9. Vấn đề chung

| # | Vấn đề | Mức độ | Màn hình |
|---|--------|--------|---------|
| 1 | `page.overlay.append/extend` gọi mỗi lần navigate, dialogs tích lũy | Cao | Members, Memberships, Equipment |
| 2 | Không có loading state khi fetch data | Trung bình | Tất cả |
| 3 | Không có empty state đẹp khi bảng trống | Thấp | Members, Memberships |
| 4 | Header search bar không có chức năng | Trung bình | Global |
| 5 | Không có màn hình login/auth | Cao | Global |
| 6 | Notification button không có chức năng | Thấp | Global |
| 7 | Không có breadcrumb/page title trong header | Thấp | Global |
| 8 | Filter active state không visual feedback | Trung bình | Equipment |

---

## 10. Đánh giá tổng thể

### Điểm mạnh
- Design system (`theme.py`) nhất quán, dễ mở rộng
- Màu sắc semantic rõ ràng cho các trạng thái
- Tất cả màn hình đã kết nối database thực
- CRUD hoàn chỉnh cho Members, Equipment, Memberships
- Layout responsive hợp lý với sidebar cố định

### Điểm cần cải thiện
- Một số UI element chỉ là trang trí (header search, notification, "View All" links)
- Overlay dialog bị leak khi navigate nhiều lần
- Không có authentication layer
- Cần thêm loading/empty states

### Đánh giá theo màn hình

| Màn hình | Hoàn thiện | Chức năng | UI/UX |
|---------|-----------|----------|-------|
| Dashboard | ★★★★☆ | ★★★★☆ | ★★★★★ |
| Members | ★★★★☆ | ★★★★☆ | ★★★★☆ |
| Memberships | ★★★☆☆ | ★★★☆☆ | ★★★★☆ |
| Equipment | ★★★★☆ | ★★★★☆ | ★★★☆☆ |
| Reports | ★★★☆☆ | ★★★☆☆ | ★★★☆☆ |
| Sidebar | ★★★★☆ | ★★★★☆ | ★★★★☆ |
| Header | ★★☆☆☆ | ★★☆☆☆ | ★★★★☆ |

**Tổng thể: 7/10** — UI có nền tảng tốt, design đẹp và nhất quán. Cần hoàn thiện các chức năng còn thiếu và fix vấn đề overlay leak.

---

*Báo cáo tạo tự động bởi Claude Code — 2026-03-20 18:48*
