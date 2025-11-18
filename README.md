# BioData Maker - HTML/CSS/JavaScript Version

## 📋 Overview

This is a **pure HTML, CSS, and JavaScript** conversion of the React-based BioData Maker application. It allows users to create professional marriage biodata with multiple templates, without requiring any build tools or frameworks.

## 🎯 Features

### ✅ Converted Features

- **Home Page** with animated hero section, template gallery, features, and FAQ
- **User Authentication** (Login/Register) with token-based auth
- **Dynamic Biodata Form** with:
  - Drag-and-drop field reordering (using SortableJS)
  - Custom field addition/deletion
  - Editable field labels
  - Mandatory field protection
  - Profile image upload with preview
  - LocalStorage auto-save
- **Template Selection** with preview
- **PDF Generation** using html2canvas and jsPDF
- **Payment/Upgrade System** with UPI verification
- **Biodata List** view
- **Premium Features** gating

### 🔄 Technical Stack

- **Frontend**: Pure HTML5, CSS3, JavaScript (ES6+)
- **Libraries**:
  - SortableJS (drag-and-drop)
  - html2canvas (screenshot)
  - jsPDF (PDF generation)
- **Backend API**: Django REST Framework (unchanged from original)
- **Storage**: LocalStorage for form data persistence

## 📁 Project Structure

```
html-version/
├── index.html                 # Home page
├── login.html                 # Authentication page
├── biodata-form.html          # Biodata creation form
├── template-page.html         # Template selection and preview
├── upgrade.html               # Premium upgrade page
├── biodata-list.html          # List of all biodatas
├── css/
│   ├── styles.css            # Global styles and utilities
│   ├── home.css              # Home page specific styles
│   └── biodata-form.css      # Form page specific styles
├── js/
│   ├── utils.js              # Utility functions
│   ├── api.js                # API client (Fetch API)
│   ├── home.js               # Home page logic
│   ├── login.js              # Authentication logic
│   ├── biodata-form.js       # Form builder logic
│   ├── template-page.js      # Template and PDF generation
│   ├── upgrade.js            # Payment verification
│   └── biodata-list.js       # Biodata listing
└── assets/                    # Images and static files
```

## 🚀 Getting Started

### Prerequisites

- A modern web browser (Chrome, Firefox, Safari, Edge)
- Backend API running (Django server)

### Installation

1. **No build process required!** Just open the files in a browser.

2. **Backend Setup** (if not already running):

   ```bash
   cd ../backend
   python manage.py runserver
   ```

3. **Open the application**:

   - Simply open `index.html` in your web browser
   - OR use a local server:

     ```bash
     # Using Python 3
     python -m http.server 8080

     # Using Node.js (if you have it)
     npx serve

     # Using VS Code Live Server extension
     Right-click index.html → Open with Live Server
     ```

4. **Access the app**:
   ```
   http://localhost:8080/index.html
   ```

## 📖 Usage Guide

### 1. Home Page (`index.html`)

- View template previews
- Navigate to create biodata
- Access login/upgrade

### 2. Login (`login.html`)

- Toggle between Login/Register
- Authentication with backend API
- Token stored in localStorage

### 3. Create Biodata (`biodata-form.html`)

- **Add Profile Photo**: Click "Upload Profile Photo"
- **Fill Sections**:
  - Personal Details (mandatory fields marked with \*)
  - Family Details
  - Habits & Declaration
- **Customize**:
  - Drag fields to reorder
  - Edit field labels (non-mandatory only)
  - Add custom fields with "Add Field" button
  - Delete unwanted fields (non-mandatory only)
- **Auto-save**: Form data saved to localStorage every 5 seconds
- **Submit**: Click "Generate Biodata" to proceed to templates

### 4. Template Selection (`template-page.html`)

- Choose from available templates
- Preview your biodata
- **Download Options**:
  - ☑️ Include Watermark
  - ☑️ Single Page (fit to A4)
- Click "Download Current Template" to generate PDF

### 5. Upgrade (`upgrade.html`)

- View payment instructions
- Scan UPI QR code
- Submit transaction ID
- Upload payment screenshot (optional)

### 6. Biodata List (`biodata-list.html`)

- View all submitted biodatas
- See profile images and details

## 🔧 Configuration

### API Base URL

Edit `js/api.js` to change the backend URL:

```javascript
const API_BASE_URL = "http://127.0.0.1:8000"; // Change this
```

### Mandatory Fields

Edit `js/biodata-form.js` to modify mandatory fields:

```javascript
const mandatoryFields = {
  PersonalDetails: ["name", "date_of_birth", "place_of_birth"],
  FamilyDetails: ["father_name", "mother_name"],
  HabitsDeclaration: [],
};
```

## 🎨 Customization

### Styling

- **Global styles**: Edit `css/styles.css`
- **Colors**: Modify CSS variables in `:root`
- **Components**: Add custom CSS classes

### Form Fields

- Initial fields defined in `js/biodata-form.js`
- Modify `initialFormData` object to add/remove default fields

### Templates

- Templates rendered in `js/template-page.js`
- Modify `renderTemplate()` function to customize layout

## 🔐 Security Notes

1. **Token Storage**: Auth tokens stored in localStorage
2. **API Calls**: All requests include Authorization header
3. **Auto-logout**: 401 responses trigger automatic logout
4. **CORS**: Ensure backend allows frontend origin

## 📱 Browser Compatibility

| Browser | Supported | Notes                   |
| ------- | --------- | ----------------------- |
| Chrome  | ✅        | Fully tested            |
| Firefox | ✅        | Fully tested            |
| Safari  | ✅        | Requires modern version |
| Edge    | ✅        | Chromium-based          |
| IE11    | ❌        | Not supported           |

## 🐛 Troubleshooting

### Common Issues

**1. "Failed to fetch" errors**

- Ensure backend server is running on `http://127.0.0.1:8000`
- Check browser console for CORS errors
- Verify API endpoints in `js/api.js`

**2. PDF download not working**

- Check if html2canvas and jsPDF are loaded
- View browser console for errors
- Ensure template content is visible

**3. Form data not saving**

- Check localStorage quota
- Clear localStorage if corrupted: `localStorage.clear()`
- Check browser console for errors

**4. Images not displaying**

- Verify image paths in `assets/` folder
- Check if images exist from React project
- Copy images from `../src/assets/` to `assets/`

**5. Drag-and-drop not working**

- Ensure SortableJS CDN is loading
- Check browser console for errors
- Verify `.drag-handle` class exists on elements

## 📦 Dependencies

### External Libraries (CDN)

```html
<!-- Drag and Drop -->
<script src="https://cdn.jsdelivr.net/npm/sortablejs@latest/Sortable.min.js"></script>

<!-- PDF Generation -->
<script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"></script>
```

### Local Storage Data

- `token`: Authentication token
- `username`: Logged-in username
- `biodataForm`: Form data with field order and image preview
- `formDataForTemplate`: Processed data for template rendering

## 🔄 Migration from React

### Key Differences

1. **No Build Step**: Direct HTML/CSS/JS, no compilation
2. **No React Components**: Pure functions and DOM manipulation
3. **SortableJS**: Replaces `@hello-pangea/dnd`
4. **Fetch API**: Replaces Axios
5. **CSS Classes**: Custom utility classes replace Tailwind
6. **File Structure**: Flat structure vs component-based

### What Changed

- ❌ JSX → ✅ HTML strings and DOM APIs
- ❌ React Hooks → ✅ Event listeners and functions
- ❌ React Router → ✅ Multi-page navigation
- ❌ Framer Motion → ✅ CSS animations
- ❌ Tailwind → ✅ Custom CSS utilities

### What Stayed the Same

- ✅ Backend API (unchanged)
- ✅ Authentication flow
- ✅ Form structure
- ✅ PDF generation logic
- ✅ LocalStorage usage

## 📝 License

Same as the original React project.

## 🤝 Contributing

1. Test changes in multiple browsers
2. Maintain vanilla JS (no frameworks)
3. Follow existing code style
4. Update README if adding features

## 📞 Support

For issues with:

- **Frontend**: Check browser console and network tab
- **Backend**: Check Django server logs
- **PDF Generation**: Verify html2canvas and jsPDF versions

## 🎉 Success!

Your BioData Maker is now running on pure HTML/CSS/JavaScript!

**Next Steps**:

1. Copy images from React `src/assets/` to `assets/` folder
2. Test all features in your target browsers
3. Customize styles in `css/styles.css`
4. Deploy to any static hosting (no build required!)

---

**Note**: This conversion maintains feature parity with the React version while eliminating all build dependencies. Perfect for simple deployments or learning purposes!
