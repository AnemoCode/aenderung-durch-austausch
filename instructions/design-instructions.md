Overlytics Design System & Layout Specifications

This document provides exact instructions for replicating the "Overlytics Dashboard" design. It is intended to be used as a master prompt for AI design and UI generation tools.

1. Global Design Tokens

1.1. Color Palette

The design relies on a strict 5-color palette, applied across the entire application to ensure a cohesive, professional, and slightly organic SaaS look.

Viridian (#344945):

Role: Primary Dark, Sidebar Background, Primary Text, Primary Buttons, Active Chart Lines.

Usage: The dominant high-contrast color. Used for headings, main text, the left sidebar, and primary call-to-action buttons.

Shell (#F7F5F1):

Role: Global App Background, Secondary Element Backgrounds.

Usage: The main canvas background (instead of pure white or light gray). Also used for search bars, table headers, and subdued container backgrounds.

Stone (#E0DCD1):

Role: Borders, Dividers, Subdued Text/Icons.

Usage: Used for all card borders, table dividers, the header's bottom border, and inactive/hover states in the sidebar.

Sky (#D5E3E8):

Role: Positive Accent, Soft Highlights.

Usage: "Active" or "OK" status badges, primary icon backgrounds in stat cards, active icon colors in the sidebar.

Honeydew (#E4E3BC):

Role: Warning Accent, Avatar Backgrounds, Secondary Highlights.

Usage: "Auth Error" or warning badges, user avatar background, secondary icon backgrounds in stat cards.

Utility Colors:

White (#FFFFFF): Used strictly for Card/Container backgrounds floating above the Shell app background.

Rose/Red (#F43F5E): Used sparingly for notification dots.

1.2. Typography & Styling

Font Family: Standard sans-serif (Inter, Roboto, or system-ui).

Border Radius:

Cards/Containers: Large (12px / rounded-xl).

Buttons/Inputs/Small Badges: Medium (6px / rounded-md).

Shadows: Subtle, low-opacity drop shadows on all white cards and buttons to lift them off the #F7F5F1 background.

2. Global App Shell (Layout)

The application uses a standard dashboard split: a fixed Left Sidebar and a dynamic Right Content Area.

2.1. Left Sidebar

Dimensions: Fixed width of 256px (w-64), full viewport height (h-screen). Hidden on mobile.

Background: Solid Viridian (#344945).

Header: 64px height (h-16), bottom border of #E0DCD1 at 20% opacity. Contains the App Icon (Sky #D5E3E8) and "Overlytics" logotype (Shell #F7F5F1, bold, 20px).

Navigation:

List of items: Übersicht, Projekte, Gruppen, Einstellungen.

Inactive Item: Text #E0DCD1 at 70% opacity. Hover effect adds a 5% opacity white/light background.

Active Item: Background #E0DCD1 at 10% opacity, Text #F7F5F1, Icon Sky (#D5E3E8).

Footer (User Profile): Top border #E0DCD1 at 20% opacity. Contains an Avatar (Circle, Bg: Honeydew #E4E3BC, Text: Viridian #344945), User Name (#F7F5F1), Plan ("Free Plan", #E0DCD1 at 70%), and a subtle "Logout" button.

2.2. Top Header (Content Area)

Dimensions: 64px height (h-16), spans remaining width. Sticky at the top.

Background: Solid White (#FFFFFF).

Border: Bottom border Solid Stone (#E0DCD1).

Left Content: A Search Input. Background is Shell (#F7F5F1), border is Stone (#E0DCD1) at 50% opacity. Text/Icon are Viridian at 50% opacity.

Right Content:

Notification Bell icon (Viridian at 60% opacity) with a small Rose/Red dot on the top right.

Primary Action Button ("Projekt tracken"): Solid Viridian (#344945), Text Shell (#F7F5F1), rounded corners (6px).

3. Page-Specific Layouts

The main content area has a maximum width of 80rem (max-w-7xl), centered, with 24px padding (p-6).

3.1. Dashboard (Übersicht) Tab

Page Header: Title (24px, bold, Viridian), Subtitle (14px, Viridian at 60% opacity). Right-aligned "Jetzt synchronisieren" secondary button (White bg, Stone border, Viridian text).

Stats Row (4 Columns):

Grid of 4 white cards.

Content: Label (Viridian 60%), Large Value (Viridian, Bold), Trend percentage.

Right side of card: A prominent Icon inside a colored square with rounded edges.

Icon Colors: Card 1 (Bg: Sky 40%), Card 2 (Bg: Honeydew 50%), Card 3 (Bg: Stone 50%), Card 4 (Bg: Shell).

Charts Row (2 Columns):

Left (2/3 width): "Schreibfortschritt" Area Chart. White card, Stone border. The chart line and area fill use Viridian (#344945) with a gradient fade to transparent at the bottom.

Right (1/3 width): "Git Zugangsdaten" Card. Contains two vertically stacked info boxes. Box 1 ("Token aktiv"): Sky background at 30% opacity, Sky border. Box 2 ("Verknüpfte Email"): Shell background, Stone border.

Table Container ("Verknüpfte Projekte"):

White card, Stone border.

Table Header Row: Shell (#F7F5F1) background, bottom border Stone (#E0DCD1). Text is uppercase, 12px, Viridian at 70%.

Table Body Rows: White background, dividing borders Stone at 50%. Hovering a row changes its background to Shell at 80% opacity.

Status Badges: "Aktiv" (Sky bg at 70%, Viridian text). "Auth Error" (Honeydew bg, Viridian text).

3.2. Projects (Projekte) Tab

Page Header: Title and subtitle matching the Dashboard style.

Grid Layout: Displays projects as cards. 1 column on mobile, 2 on tablet, 3 on desktop.

Project Card Design:

Background: White (#FFFFFF). Border: Stone (#E0DCD1). Hover state darkens border to Viridian at 20%.

Top Section: Project Title (Bold, Viridian), Git URL (Viridian 50%), "More" vertical dots icon. Bottom border Stone 50%.

Middle Section: Flex layout. Row 1: "Status" label + Status Badge (Sky or Honeydew). Row 2: 2-column grid for "Wörter" and "Seiten" counts (Numbers in bold Viridian). This grid has top/bottom borders of Stone 30%.

Bottom Section: Last sync text (Viridian 50%) + Action icon buttons (Sync, Edit) that have a hover background of Shell (#F7F5F1).

3.3. Groups (Gruppen) Tab

Page Header: Title, subtitle, and a "Neue Gruppe" primary button (Viridian bg, Shell text).

Table Layout: A single, full-width table contained inside a white card with a Stone border.

Table Styling: Matches the Dashboard table (Header is Shell bg, borders are Stone).

Row Elements:

Group Avatar: A 32x32px rounded square (Bg: Sky at 50%, Border: Sky) containing the first letter of the group name in Viridian.

Role Badges: "Admin" (Bg: Viridian, Text: Shell). "Member" (Bg: Stone 50%, Text: Viridian).

Action: Settings icon button aligned to the right.