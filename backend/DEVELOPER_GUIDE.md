# CrucibAI Developer Guide

## Project Structure

```
crucibai/
├── backend/
│   ├── server.py          # Main FastAPI app
│   ├── error_handlers.py  # Error handling utilities
│   ├── middleware.py      # Security middleware
│   ├── validators.py      # Input validation
│   ├── query_optimizer.py # Database optimization
│   └── requirements.txt    # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── pages/         # Page components
│   │   ├── components/    # Reusable components
│   │   ├── utils/         # Utility functions
│   │   ├── styles/        # CSS files
│   │   └── App.jsx        # Main app component
│   └── package.json       # Node dependencies
└── README.md
```

## Development Workflow

### 1. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
```

### 2. Make Changes

- Write code following the style guide
- Add tests for new functionality
- Update documentation

### 3. Test Your Changes

```bash
# Backend tests
cd backend
pytest test_suite.py -v

# Frontend tests
cd frontend
npm test
```

### 4. Commit and Push

```bash
git add .
git commit -m "feat: description of your changes"
git push origin feature/your-feature-name
```

### 5. Create Pull Request

Create a PR on GitHub with:
- Clear description of changes
- Link to related issues
- Screenshots (if UI changes)

## Code Style

### Python

- Follow PEP 8
- Use type hints
- Max line length: 100 characters
- Use meaningful variable names

```python
def get_user_by_email(email: str):
    # Get user by email address
    return db.users.find_one({'email': email})
```

### JavaScript/React

- Use ES6+ syntax
- Use functional components with hooks
- Use meaningful component names
- Add JSDoc comments

```javascript
/**
 * UserProfile component
 * @param {string} userId - User ID
 * @returns {JSX.Element}
 */
export const UserProfile = ({ userId }) => {
  const [user, setUser] = useState(null);
  
  useEffect(() => {
    fetchUser(userId);
  }, [userId]);
  
  return <div>{user?.name}</div>;
};
```

## Testing

### Backend Tests

```bash
pytest test_suite.py -v --cov=.
```

### Frontend Tests

```bash
npm test -- --coverage
```

### E2E Tests

```bash
npm run test:e2e
```

## Documentation

- Update README.md for major changes
- Add comments for complex logic
- Keep API documentation up-to-date
- Document new environment variables

## Performance Tips

1. **Frontend**
   - Use React.memo for expensive components
   - Implement code splitting
   - Optimize images
   - Use lazy loading

2. **Backend**
   - Add database indexes
   - Use query caching
   - Implement pagination
   - Use connection pooling

3. **Database**
   - Monitor slow queries
   - Optimize aggregation pipelines
   - Use appropriate data types
   - Archive old data

## Debugging

### Backend

```python
# Add logging
import logging
logger = logging.getLogger(__name__)
logger.debug(f"Variable: {variable}")

# Use debugger
import pdb; pdb.set_trace()
```

### Frontend

```javascript
// Use console
console.log('Debug:', variable);
console.error('Error:', error);

// Use debugger
debugger;
```

## Common Issues

### Import Errors

Make sure all imports are correct and modules are installed.

### Type Errors

Use type hints (Python) and TypeScript for better error detection.

### Performance Issues

Profile code using:
- Python: `cProfile`
- JavaScript: Chrome DevTools

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [MongoDB Documentation](https://docs.mongodb.com/)
- [Tailwind CSS](https://tailwindcss.com/)

## Getting Help

- Check existing issues on GitHub
- Ask in Discord community
- Email support@crucibai.com
