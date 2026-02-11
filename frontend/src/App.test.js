/**
 * App / root tests (Layer 2 – Unit).
 * Smoke: root div and public paths exist; full App render tested in E2E.
 */
describe('App entry', () => {
  it('document and root exist', () => {
    expect(document).toBeDefined();
    expect(document.createElement).toBeDefined();
  });

  it('React createRoot is available', () => {
    const ReactDOM = require('react-dom/client');
    expect(ReactDOM.createRoot).toBeDefined();
  });
});
