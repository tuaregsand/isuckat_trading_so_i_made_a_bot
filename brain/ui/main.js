document.addEventListener('DOMContentLoaded', () => {
  const startBtn = document.getElementById('startBtn');
  const stopBtn = document.getElementById('stopBtn');
  const configForm = document.getElementById('configForm');
  const currentConfigPre = document.getElementById('currentConfig');
  const statusPre = document.getElementById('status');
  const genWalletBtn = document.getElementById('genWalletBtn');
  const importWalletBtn = document.getElementById('importWalletBtn');
  const walletPre = document.getElementById('wallet');
  
  function toggleButtons(running) {
    startBtn.disabled = running;
    stopBtn.disabled = !running;
  }
  
  async function loadConfig() {
    try {
      const res = await fetch('/config');
      const cfg = await res.json();
      currentConfigPre.textContent = JSON.stringify(cfg, null, 2);
      document.getElementById('maxDailyLoss').value = cfg.max_daily_loss_sol;
      document.getElementById('tokenBlacklist').value = (cfg.token_blacklist || []).join(',');
      document.getElementById('minLiquidity').value = cfg.min_liquidity_sol;
      document.getElementById('maxTradeAmount').value = cfg.max_trade_amount_sol;
      document.getElementById('slippage').value = cfg.slippage_bps;
    } catch (e) {
      console.error('Failed to load config', e);
    }
  }
  
  async function loadStatus() {
    try {
      const res = await fetch('/status');
      const st = await res.json();
      statusPre.textContent = JSON.stringify(st, null, 2);
      toggleButtons(st.running);
    } catch (e) {
      console.error('Failed to load status', e);
    }
  }
  
  startBtn.onclick = async () => {
    await fetch('/start', { method: 'POST' });
    loadStatus();
  };
  stopBtn.onclick = async () => {
    await fetch('/stop', { method: 'POST' });
    loadStatus();
  };
  
  configForm.onsubmit = async (e) => {
    e.preventDefault();
    const body = {
      max_daily_loss_sol: parseFloat(document.getElementById('maxDailyLoss').value),
      token_blacklist: document.getElementById('tokenBlacklist').value
        .split(',')
        .map(s => s.trim())
        .filter(s => s),
      min_liquidity_sol: parseFloat(document.getElementById('minLiquidity').value),
      max_trade_amount_sol: parseFloat(document.getElementById('maxTradeAmount').value),
      slippage_bps: parseInt(document.getElementById('slippage').value, 10),
    };
    try {
      await fetch('/config', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });
      loadConfig();
    } catch (e) {
      console.error('Failed to update config', e);
    }
  };
  
  genWalletBtn.onclick = async () => {
    try {
      const res = await fetch('/wallet', { method: 'POST' });
      const data = await res.json();
      walletPre.textContent = JSON.stringify(data, null, 2);
    } catch (e) {
      console.error('Failed to generate wallet', e);
    }
  };
  
  importWalletBtn.onclick = async () => {
    const input = prompt('Enter your BIP39 mnemonic phrase or Secret Key JSON array:');
    if (!input) return;
    // Determine if input is JSON array (secret key) or mnemonic
    let body;
    try {
      const parsed = JSON.parse(input);
      if (Array.isArray(parsed)) {
        body = { secret_key: parsed };
      } else if (parsed.mnemonic) {
        body = { mnemonic: parsed.mnemonic };
      } else {
        body = { mnemonic: input };
      }
    } catch {
      body = { mnemonic: input };
    }
    try {
      const res = await fetch('/wallet/import', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });
      const data = await res.json();
      walletPre.textContent = JSON.stringify(data, null, 2);
    } catch (e) {
      console.error('Failed to import wallet', e);
    }
  };
  
  loadConfig();
  loadStatus();
  setInterval(loadStatus, 5000);
  
  const ws = new WebSocket(
    (location.protocol === 'https:' ? 'wss://' : 'ws://') + location.host + '/stream'
  );
  ws.onmessage = (evt) => {
    try {
      const msg = JSON.parse(evt.data);
      statusPre.textContent = JSON.stringify(msg, null, 2);
      if (msg.running !== undefined) toggleButtons(msg.running);
    } catch {
      statusPre.textContent = evt.data;
    }
  };
});