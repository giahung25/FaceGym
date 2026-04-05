# ============================================================================
# FILE: gui/theme.py
# MỤC ĐÍCH: Lưu trữ các HẰNG SỐ THIẾT KẾ (Design Tokens) cho toàn bộ giao diện.
#            Mọi file GUI đều import từ đây để dùng — giúp đồng bộ giao diện.
#
# TẠI SAO DÙNG DESIGN TOKENS?
#   - Thay đổi 1 chỗ → ảnh hưởng TOÀN BỘ app (VD: đổi theme.ORANGE → tất cả nút đổi màu)
#   - Tránh "magic number" — thay vì gõ "#F97316" khắp nơi, dùng theme.ORANGE
#   - Dễ đọc code: theme.FONT_LG rõ ràng hơn số 16
# ============================================================================

# ── Bảng màu (Color Palette) ─────────────────────────────────────────────────
# Giá trị HEX: "#RRGGBB" — Red, Green, Blue (mỗi cặp từ 00 đến FF)
ORANGE = "#F97316"              # Màu cam chính — dùng cho nút, icon, highlight
ORANGE_LIGHT = "#FED7AA"        # Cam nhạt — dùng làm nền cho badge/icon
SIDEBAR_BG = "#1C1C2E"          # Xanh đen — nền sidebar
SIDEBAR_ITEM_HOVER = "#2D2D44"  # Xanh đen nhạt hơn — khi hover menu item
WHITE = "#FFFFFF"               # Trắng
BG = "#F5F5F5"                  # Xám nhạt — nền chính của app
CARD_BG = "#FFFFFF"             # Trắng — nền card
GREEN = "#22C55E"               # Xanh lá — trạng thái tốt (active, working)
GREEN_LIGHT = "#DCFCE7"         # Xanh nhạt — nền badge xanh
AMBER = "#F59E0B"               # Vàng cam — trạng thái cảnh báo (sắp hết hạn)
AMBER_LIGHT = "#FEF3C7"         # Vàng nhạt — nền badge vàng
RED = "#EF4444"                 # Đỏ — trạng thái nguy hiểm (hỏng, lỗi)
RED_LIGHT = "#FEE2E2"           # Đỏ nhạt — nền badge đỏ
BLUE = "#3B82F6"                # Xanh dương — thông tin, liên kết
BLUE_LIGHT = "#DBEAFE"          # Xanh dương nhạt
GRAY = "#6B7280"                # Xám — text phụ, label
GRAY_LIGHT = "#E5E7EB"          # Xám nhạt — progress bar nền
TEXT_PRIMARY = "#111827"         # Đen đậm — text chính
TEXT_SECONDARY = "#6B7280"       # Xám — text phụ
BORDER = "#E5E7EB"              # Xám nhạt — viền, đường kẻ

# ── Kích thước chữ (Typography) ──────────────────────────────────────────────
# Đơn vị: pixel (px)
FONT_XS = 11    # Extra Small — badge, label nhỏ
FONT_SM = 12    # Small — text thường, nội dung bảng
FONT_MD = 14    # Medium — text mặc định, nút bấm
FONT_LG = 16    # Large — tiêu đề phụ
FONT_XL = 18    # Extra Large — tiêu đề section
FONT_2XL = 22   # 2X Large — tiêu đề trang
FONT_3XL = 28   # 3X Large — số liệu lớn (KPI)

# ── Khoảng cách (Spacing / Padding) ──────────────────────────────────────────
# Dùng cho padding, margin, spacing giữa các phần tử
PAD_XS = 4      # 4px — khoảng cách rất nhỏ
PAD_SM = 8      # 8px — khoảng cách nhỏ
PAD_MD = 12     # 12px — khoảng cách trung bình
PAD_LG = 16     # 16px — khoảng cách lớn
PAD_XL = 20     # 20px — khoảng cách rất lớn
PAD_2XL = 24    # 24px — padding chính của content area

# ── Kích thước cố định (Sizing) ──────────────────────────────────────────────
SIDEBAR_WIDTH = 220    # Chiều rộng sidebar: 220px (cố định, không co giãn)
HEADER_HEIGHT = 64     # Chiều cao header: 64px
CARD_RADIUS = 12       # Bo góc card: 12px (làm card tròn hơn)
BUTTON_RADIUS = 8      # Bo góc nút: 8px
BADGE_RADIUS = 20      # Bo góc badge: 20px (gần như hình tròn)
