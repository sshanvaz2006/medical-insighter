# Quick Start Guide - Medical Insight Engine Frontend

## 5-Minute Setup

### 1. Install Dependencies
```bash
cd frontend
npm install
```

### 2. Configure Environment
```bash
cp .env.example .env
# Edit .env and set VITE_API_URL to your backend
```

### 3. Start Development Server
```bash
npm run dev
```
Open `http://localhost:3000` in your browser.

---

## Common Commands

```bash
# Development
npm run dev              # Start dev server
npm run lint            # Check code quality

# Production
npm run build           # Build for production
npm run preview         # Preview production build
```

---

## Project Structure Quick Reference

```
frontend/src/
├── index.js                 # App entry point
├── App.jsx                  # Main app (routing)
├── components/              # React components
├── context/                 # State management (Auth, Theme)
├── hooks/                   # Custom React hooks
├── services/                # API services
├── utils/                   # Helper functions
└── styles/                  # Global CSS
```

---

## Key Features Overview

### 1. **Authentication**
- Login/Register pages
- Protected routes
- JWT token management
- Auto-logout on 401

### 2. **Dashboard**
- Statistics cards
- Recent activity
- Quick actions

### 3. **Reports**
- List with pagination
- Search and filter
- Detail view
- Delete functionality

### 4. **Document Upload**
- Drag-and-drop
- File validation
- Progress tracking

### 5. **Analytics**
- Trend charts
- Key insights
- Data visualization

---

## Testing the App

### Test Account (Backend must support)
```
Email: test@example.com
Password: Test@123456
```

### Login Flow
1. Go to `/auth/login`
2. Enter credentials
3. Redirected to dashboard
4. Click logout to test

### Create Report Flow
1. Go to `/upload`
2. Drag files or select
3. Click upload
4. View in `/reports`

---

## API Configuration

Backend should have these endpoints:

```
POST   /api/auth/login
POST   /api/auth/register
POST   /api/auth/logout
GET    /api/auth/me

GET    /api/reports
POST   /api/reports
GET    /api/reports/:id
PUT    /api/reports/:id
DELETE /api/reports/:id

GET    /api/analytics/stats
GET    /api/analytics/trends
GET    /api/analytics/insights
```

---

## Troubleshooting

### CORS Error
```
Check: VITE_API_URL is correct
Check: Backend CORS is configured
```

### Can't Login
```
Check: Backend is running
Check: API_URL points to correct server
Check: User exists in database
```

### Styling Issues
```
Check: npm install ran successfully
Check: Tailwind CSS processing
Restart: npm run dev
```

### Port Already in Use
```bash
# Use different port
npm run dev -- --port 3001
```

---

## File Organization

### Add New Component
```javascript
// src/components/Feature/NewComponent.jsx
import React from 'react';

const NewComponent = () => {
  return <div>New Component</div>;
};

export default NewComponent;
```

### Add New Service
```javascript
// src/services/feature.js
import api from './api';

export const featureService = {
  async getData() {
    const response = await api.get('/endpoint');
    return response.data;
  }
};
```

### Add New Hook
```javascript
// src/hooks/useFeature.js
import { useState } from 'react';

export const useFeature = () => {
  const [data, setData] = useState(null);
  return { data };
};
```

---

## Styling

### Using Tailwind Classes
```jsx
<div className="bg-blue-500 text-white p-4 rounded-lg">
  Styled with Tailwind
</div>
```

### Dark Mode
```jsx
<div className="bg-white dark:bg-gray-800">
  Auto supports dark mode
</div>
```

### Custom CSS
```css
/* src/styles/custom.css */
.custom-class {
  /* Custom styles */
}
```

---

## Form Example

```jsx
import { useForm } from 'react-hook-form';
import { validateEmail } from '../utils/validation';

export function MyForm() {
  const { register, handleSubmit, formState: { errors } } = useForm();

  const onSubmit = async (data) => {
    // Handle form submission
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <input
        {...register('email', {
          required: 'Email required',
          validate: (v) => validateEmail(v) || 'Invalid email'
        })}
      />
      {errors.email && <p>{errors.email.message}</p>}
      <button type="submit">Submit</button>
    </form>
  );
}
```

---

## API Call Example

```jsx
import { reportsService } from '../services/reports';
import { useEffect, useState } from 'react';

export function ReportComponent() {
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchReports = async () => {
      try {
        const data = await reportsService.getReports();
        setReports(data);
      } catch (error) {
        console.error(error);
      } finally {
        setLoading(false);
      }
    };

    fetchReports();
  }, []);

  if (loading) return <div>Loading...</div>;
  return <ul>{reports.map(r => <li key={r.id}>{r.title}</li>)}</ul>;
}
```

---

## Debugging Tips

### Console Logs
```javascript
// Use browser console
console.log('Value:', value);
console.error('Error:', error);
```

### Network Tab
```
Chrome DevTools > Network tab
Check API requests and responses
```

### React DevTools Extension
```
Install React DevTools browser extension
Inspect component props and state
```

---

## Performance Tips

1. **Lazy Load Components**
   - Use React.lazy() for route components

2. **Optimize Renders**
   - Use useCallback for handlers
   - Use useMemo for expensive calculations

3. **Debounce Search**
   - Already implemented with useDebounce hook

4. **Monitor Bundle Size**
   - Run npm run build
   - Check dist/ folder size

---

## Security Reminders

1. **Never store sensitive data in localStorage**
2. **Always validate user input**
3. **Use HTTPS in production**
4. **Keep dependencies updated**
5. **Use strong passwords**
6. **Validate on both client and server**

---

## Resources

- [React Documentation](https://react.dev)
- [Tailwind CSS](https://tailwindcss.com)
- [React Router](https://reactrouter.com)
- [Vite](https://vitejs.dev)
- [Axios](https://axios-http.com)

---

## Getting Help

1. Check browser console for errors
2. Check Network tab for API calls
3. Review component props/state
4. Check documentation
5. Contact support team

---

**Ready to code?** 🚀

Start the dev server and begin building amazing features!

```bash
npm run dev
```

Happy coding! 💻
