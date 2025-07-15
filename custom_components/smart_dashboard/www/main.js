class SmartDashboard {
  constructor(url, token) {
    this.url = url.replace(/\/$/, '');
    this.token = token;
    this.state = [];
    this.interval = null;
    this.lazyInit = false;
    this.lazyLoad = false;
    this.observer = null;
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

  _updateElement(el) {
    const entity = el.dataset.entityId;
    const st = this.state.find(s => s.entity_id === entity);
    if (st) {
      el.textContent = st.state;
    }
  }

  _setupLazy(elements) {
    if (this.observer) return;
    this.observer = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          this._updateElement(entry.target);
        }
      });
    }, { rootMargin: '100px' });
    elements.forEach(el => this.observer.observe(el));
  }

  updateDom() {
    const elements = document.querySelectorAll('[data-entity-id]');
    if (!this.lazyInit) {
      this.lazyLoad = elements.length > 500;
      this.lazyInit = true;
    }
    if (this.lazyLoad) {
      this._setupLazy(elements);
      elements.forEach(el => {
        if (this.observer && el.getBoundingClientRect) {
          const rect = el.getBoundingClientRect();
          if (rect.bottom >= 0 && rect.top <= window.innerHeight) {
            this._updateElement(el);
          }
        }
      });
    } else {
      elements.forEach(el => this._updateElement(el));
    }
  }

  evaluateCondition(expr, user = null) {
    const state = id => {
      const st = this.state.find(s => s.entity_id === id);
      return st ? st.state : undefined;
    };
    try {
      const fn = new Function('state', 'user', `"use strict"; return (${expr});`);
      return Boolean(fn(state, user));
    } catch (err) {
      console.error('Failed evaluating condition', expr, err);
      return false;
    }
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

