# Tailwind CSS Quick Reference - Pastel Play

## Color Classes

### Text Colors

```
text-primary          → #243B4A (deep slate)
text-secondary        → #5A6F7D (muted)
text-muted            → #8A9AAB (very muted)
text-white            → #FFFFFF (on dark backgrounds)
```

### Background Colors

```
bg-primary            → #A8E6CF (mint)
bg-primary-light      → #D5F5E8
bg-primary-dark       → #7DD9BB

bg-secondary          → #FFD3B6 (peach)
bg-secondary-light    → #FFE5D9
bg-secondary-dark     → #FFB894

bg-accent             → #FFAAA5 (coral)
bg-accent-light       → #FFCCC7
bg-accent-dark        → #FF8A84

bg-neutral            → #FFFDF8 (off-white)
bg-surface            → #FFFFFF (white)
bg-surface-alt        → #FFFBF7

bg-default            → #FFFDF8
bg-card               → #FFFFFF
bg-hover              → #FFFBF7
```

### Border Colors

```
border-primary        → #A8E6CF
border-secondary      → #FFD3B6
border-accent         → #FFAAA5
border                → #E8D5C8
border-light          → #F0E8E0
```

---

## Component Classes

### Buttons

```html
<!-- Primary Button (Mint) -->
<button class="btn-primary">Click Me</button>

<!-- Secondary Button (Peach) -->
<button class="btn-secondary">Click Me</button>

<!-- Accent Button (Coral) -->
<button class="btn-accent">Click Me</button>

<!-- Outline Button -->
<button class="btn-outline">Click Me</button>

<!-- Button Sizes -->
<button class="btn-primary text-xs px-2 py-1">Tiny</button>
<button class="btn-primary text-sm px-4 py-2">Small</button>
<button class="btn-primary px-6 py-3">Regular</button>
<button class="btn-primary px-8 py-4">Large</button>

<!-- Full Width Button -->
<button class="btn-primary w-full">Full Width</button>
```

### Cards

```html
<!-- Basic Card -->
<div class="card">
  <h3 class="text-lg font-bold">Card Title</h3>
  <p>Card content goes here</p>
</div>

<!-- With Custom Spacing -->
<div class="card p-8">...</div>

<!-- With Custom Width -->
<div class="card max-w-sm">...</div>
<div class="card max-w-md">...</div>
<div class="card max-w-lg">...</div>
```

### Badges

```html
<!-- Default Badge (Secondary) -->
<span class="badge">Badge Text</span>

<!-- Accent Badge -->
<span class="badge badge-accent">Badge Text</span>

<!-- Primary Badge -->
<span class="badge badge-primary">Badge Text</span>

<!-- Different Sizes -->
<span class="badge text-xs">Small</span>
<span class="badge">Regular</span>
<span class="badge text-base">Large</span>
```

### Inputs & Forms

```html
<!-- Text Input -->
<input type="text" class="input" placeholder="Enter text" />

<!-- Email Input -->
<input type="email" class="input" placeholder="your@email.com" />

<!-- Select Dropdown -->
<select class="input">
  <option>Choose one</option>
  <option>Option 1</option>
</select>

<!-- Textarea -->
<textarea class="input" rows="4" placeholder="Your message..."></textarea>

<!-- Form Group (with label) -->
<div class="space-y-2">
  <label class="text-sm font-medium text-text-primary">Label</label>
  <input type="text" class="input" />
</div>
```

### Navigation

```html
<nav class="bg-primary text-text-primary">
  <div class="flex gap-4">
    <a href="#" class="nav-item">Home</a>
    <a href="#" class="nav-item active">Current</a>
    <a href="#" class="nav-item">About</a>
  </div>
</nav>
```

---

## Spacing & Layout

### Padding

```
p-sm              → 8px all sides
p-md              → 12px all sides
p-lg              → 16px all sides
p-xl              → 24px all sides
p-xxl             → 32px all sides

px-lg             → 16px left & right
py-lg             → 16px top & bottom
pt-lg             → 16px top only
pb-lg             → 16px bottom only
pl-lg             → 16px left only
pr-lg             → 16px right only
```

### Margin

```
m-lg              → 16px all sides
mx-auto           → Center horizontally
my-lg             → 16px top & bottom
mt-lg             → 16px top
mb-lg             → 16px bottom
ml-lg             → 16px left
mr-lg             → 16px right
```

### Gap (for Flexbox/Grid)

```
gap-2             → 8px
gap-4             → 16px
gap-6             → 24px
gap-8             → 32px
```

---

## Responsive Design

### Mobile-First Approach

```html
<!-- 1 column on mobile, 2 on tablet, 3 on desktop -->
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
  <div class="card">Card 1</div>
  <div class="card">Card 2</div>
  <div class="card">Card 3</div>
</div>

<!-- Hide on mobile, show on tablet+ -->
<div class="hidden md:block">Desktop only</div>

<!-- Full width on mobile, fixed on desktop -->
<div class="w-full lg:max-w-4xl">Content</div>

<!-- Larger padding on desktop -->
<div class="p-4 md:p-8 lg:p-12">Content</div>
```

### Breakpoints

```
sm               → 640px
md               → 768px
lg               → 1024px
xl               → 1280px
2xl              → 1536px
```

---

## Typography

### Font Sizes

```
text-xs           → 12px
text-sm           → 14px
text-base         → 16px (default)
text-lg           → 18px
text-xl           → 20px
text-2xl          → 24px
text-3xl          → 30px
text-4xl          → 36px
```

### Font Weight

```
font-normal       → 400
font-medium       → 500
font-bold         → 600
font-black        → 700
```

### Font Family

```
font-sans         → Segoe UI, Roboto, etc.
font-display      → Poppins (headings)
font-mono         → Monospace (code)
```

### Heading Styles

```html
<h1 class="text-4xl font-bold mb-4">Large Heading</h1>
<h2 class="text-3xl font-bold mb-3">Medium Heading</h2>
<h3 class="text-2xl font-bold mb-2">Small Heading</h3>
<h4 class="text-xl font-bold">Tiny Heading</h4>
```

---

## Flexbox & Grid

### Flexbox

```html
<!-- Row layout (default) -->
<div class="flex gap-4">
  <div>Item 1</div>
  <div>Item 2</div>
</div>

<!-- Column layout -->
<div class="flex flex-col gap-4">
  <div>Item 1</div>
  <div>Item 2</div>
</div>

<!-- Center items -->
<div class="flex items-center justify-center gap-4">
  <div>Centered</div>
</div>

<!-- Space between -->
<div class="flex justify-between">
  <div>Left</div>
  <div>Right</div>
</div>
```

### Grid

```html
<!-- Simple 3-column grid -->
<div class="grid grid-cols-3 gap-4">
  <div class="card">1</div>
  <div class="card">2</div>
  <div class="card">3</div>
</div>

<!-- Responsive grid -->
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
  <div class="card">1</div>
  <div class="card">2</div>
  <div class="card">3</div>
</div>

<!-- Auto-fit grid -->
<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
  <div class="card">1</div>
  <div class="card">2</div>
</div>
```

---

## Shadows & Borders

### Shadows

```
shadow-sm         → Subtle shadow
shadow-md         → Medium shadow
shadow-lg         → Large shadow
shadow-card       → Card-specific shadow (custom)
```

### Borders

```
border            → 1px border
border-2          → 2px border
border-4          → 4px border

border-primary    → Mint border
border-secondary  → Peach border
border-accent     → Coral border

rounded           → 4px corners
rounded-md        → 8px corners
rounded-lg        → 12px corners
rounded-xl        → 16px corners
rounded-full      → 50% (circles)
```

### Combined

```html
<!-- Card with border and shadow -->
<div class="border border-primary rounded-lg shadow-card p-6">
  <h3 class="font-bold text-text-primary">Card</h3>
  <p class="text-text-secondary">Content</p>
</div>
```

---

## Utilities

### Display

```
block             → display: block
inline            → display: inline
inline-block      → display: inline-block
hidden            → display: none
visible           → visibility: visible
```

### Opacity

```
opacity-50        → 50% opacity
opacity-75        → 75% opacity
opacity-100       → 100% opacity
```

### Transitions

```
transition        → All properties
transition-colors → Color changes only
duration-200      → 200ms duration
duration-300      → 300ms duration
ease-in           → Ease-in timing
ease-out          → Ease-out timing
```

### Hover/Focus States

```html
<button
  class="bg-primary hover:bg-primary-dark focus:ring-2 focus:ring-primary-light"
>
  Hover and focus states
</button>
```

---

## Common Patterns

### Centered Container

```html
<div class="max-w-6xl mx-auto px-6 py-12">
  <h1 class="text-4xl font-bold mb-8">Centered Content</h1>
  <p>Your content centered and padded</p>
</div>
```

### Hero Section

```html
<section class="bg-gradient-mint-to-peach py-20 px-6 text-center text-white">
  <h1 class="text-4xl font-bold mb-4">Welcome</h1>
  <p class="text-lg mb-8">Tagline here</p>
  <button class="btn-primary">Get Started</button>
</section>
```

### Dashboard Grid

```html
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
  <div class="rounded-lg p-6 bg-primary-light border border-primary">
    <p class="text-sm text-text-secondary">Label</p>
    <p class="text-3xl font-bold text-primary">42</p>
  </div>
  <!-- Repeat for other stats -->
</div>
```

### Modal/Overlay

```html
<div
  class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center"
>
  <div class="card max-w-md">
    <h3 class="text-xl font-bold mb-4">Modal Title</h3>
    <p class="mb-6">Modal content</p>
    <div class="flex gap-3">
      <button class="btn-primary flex-1">Confirm</button>
      <button class="btn-outline flex-1">Cancel</button>
    </div>
  </div>
</div>
```

---

## Tips & Tricks

1. **Use `max-w-*` for content width limits**

   ```html
   <div class="max-w-2xl mx-auto">Centered, max 42rem wide</div>
   ```

2. **Combine responsive with base classes**

   ```html
   <div class="text-base md:text-lg lg:text-xl">Responsive text</div>
   ```

3. **Use `space-y-*` for vertical spacing**

   ```html
   <div class="space-y-4">
     <div>Item 1</div>
     <div>Item 2</div>
   </div>
   ```

4. **Use `divide-*` for separators**

   ```html
   <div class="divide-y divide-border">
     <div>Top</div>
     <div>Bottom</div>
   </div>
   ```

5. **Group hover effects**
   ```html
   <div class="group card hover:shadow-lg">
     <h3 class="text-primary group-hover:text-primary-dark">
       Hover the whole card
     </h3>
   </div>
   ```

---

## Debugging

### See Generated CSS

```bash
npm run dev  # Builds and watches for changes
```

### Check what's applied

- Open browser DevTools (F12)
- Inspect element
- Look for `applied styles` with Tailwind class names

### Clear cache

```bash
# Hard refresh in browser
Ctrl+Shift+R (Windows)
Cmd+Shift+R (Mac)
```

---

**Happy Tailwind coding! 🎨💚**
