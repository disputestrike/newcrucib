/**
 * Manual mock for react-router-dom in Jest tests.
 */
const React = require('react');

const MemoryRouter = ({ children }) => React.createElement('div', null, children);
const Link = ({ to, children, ...props }) => React.createElement('a', { href: to, ...props }, children);
const useLocation = () => ({ pathname: '/', hash: '', search: '' });
const useNavigate = () => () => {};
const useSearchParams = () => [new URLSearchParams(), () => {}];
const Outlet = () => React.createElement('div', null);
const Navigate = ({ to }) => React.createElement('div', { 'data-to': to });
const useParams = () => ({});

module.exports = {
  MemoryRouter,
  Link,
  useLocation,
  useNavigate,
  useSearchParams,
  Outlet,
  Navigate,
  useParams,
  Routes: ({ children }) => React.createElement(React.Fragment, null, children),
  Route: ({ element }) => element,
  BrowserRouter: ({ children }) => React.createElement('div', null, children),
};
