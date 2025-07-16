class DwainsStyle {
  constructor() {
    document.addEventListener('DOMContentLoaded', () => {
      const header = document.querySelector('ha-header-bar');
      if (header) {
        this.addClock(header);
      }
      this.addStyles();
    });
  }

  addStyles() {
    const style = document.createElement('style');
    style.textContent = `
      hui-grid-card {
        gap: 8px !important;
      }
    `;
    document.head.appendChild(style);
  }

  addClock(header) {
    const clock = document.createElement('div');
    clock.id = 'dwains-clock';
    clock.style.marginLeft = 'auto';
    clock.style.padding = '0 16px';
    clock.style.fontWeight = 'bold';
    header.appendChild(clock);
    const update = () => {
      const now = new Date();
      clock.textContent = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    };
    update();
    setInterval(update, 60000);
  }
}
new DwainsStyle();
