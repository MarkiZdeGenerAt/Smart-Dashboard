class SmartDashboard {
  constructor(url, token) {
    this.url = url.replace(/\/$/, '');
    this.token = token;
    this.state = [];
    this.interval = null;
  }

  async fetchStates() {
    try {
      const resp = await fetch(`${this.url}/api/states`, {
        headers: { 'Authorization': `Bearer ${this.token}` }
      });
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
      this.state = await resp.json();
      this.updateDom();
    } catch(err) {
      console.error('Failed loading states:', err);
    }
  }

  updateDom() {
    document.querySelectorAll('[data-entity-id]').forEach(el => {
      const entity = el.dataset.entityId;
      const st = this.state.find(s => s.entity_id === entity);
      if (st) {
        el.textContent = st.state;
      }
    });
  }

  start(interval = 5000) {
    this.fetchStates();
    this.interval = setInterval(() => this.fetchStates(), interval);
  }

  stop() {
    if (this.interval) clearInterval(this.interval);
  }
}

window.SmartDashboard = SmartDashboard;

