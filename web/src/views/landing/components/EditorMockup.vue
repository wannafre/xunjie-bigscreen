<template>
  <section id="mockup" class="mockup-section">
    <div class="section-header">
      <span class="section-tag">在线编辑器</span>
      <h2>像 PPT 一样简单的拖拽式大屏编辑器</h2>
      <p>提供超过 100+ 种高科技图表、热力图、三维地球以及酷炫的动效素材</p>
    </div>

    <div class="editor-mockup-wrapper">
      <!-- Main Window Container -->
      <div class="editor-window">
        <!-- Top Window Bar -->
        <div class="window-titlebar">
          <div class="window-dots">
            <span class="dot red"></span>
            <span class="dot yellow"></span>
            <span class="dot green"></span>
          </div>
          <div class="window-title">智慧城市应急指挥调度大屏.vds</div>
          <div class="window-actions">
            <a-tag color="arcoblue" size="small"><icon-check-circle /> 已自动保存</a-tag>
            <button class="share-mini-btn" @click="goToConsole"><icon-share-internal /> 分享</button>
          </div>
        </div>

        <!-- Editor Body Layout -->
        <div class="editor-body">
          <!-- Left panel: Widgets -->
          <aside class="editor-left-panel">
            <div class="panel-section-title">组件库</div>
            <div class="widget-list">
              <div class="widget-item active">
                <icon-compass class="w-icon" />
                <span>3D 地图</span>
              </div>
              <div class="widget-item">
                <icon-bar-chart class="w-icon" />
                <span>柱状图表</span>
              </div>
              <div class="widget-item">
                <icon-live-broadcast class="w-icon" />
                <span>雷达扫描</span>
              </div>
              <div class="widget-item">
                <icon-common class="w-icon" />
                <span>数据指标</span>
              </div>
              <div class="widget-item">
                <icon-video-camera class="w-icon" />
                <span>视频监控</span>
              </div>
            </div>
          </aside>

          <!-- Center Canvas -->
          <main class="editor-canvas-container">
            <div class="canvas-ruler horizontal"></div>
            <div class="canvas-ruler vertical"></div>
            
            <!-- Actual Canvas Board -->
            <div class="editor-canvas">
              <!-- Grid background -->
              <div class="canvas-grid-bg"></div>

              <!-- Big Screen Content Mockup -->
              <div class="screen-layout">
                <!-- Header inside screen -->
                <div class="screen-header">
                  <div class="sh-line"></div>
                  <div class="sh-title">智慧城市物联运行监测大屏</div>
                  <div class="sh-line"></div>
                </div>

                <!-- Grid Columns -->
                <div class="screen-grid">
                  <!-- Left Charts -->
                  <div class="sg-col side-col">
                    <div class="screen-card">
                      <div class="sc-title">重点安防监控区域</div>
                      <div class="sc-chart gauge-chart">
                        <svg viewBox="0 0 100 100" class="gauge-svg">
                          <circle cx="50" cy="50" r="40" stroke="#1d263b" stroke-width="8" fill="none" />
                          <circle cx="50" cy="50" r="40" stroke="#00d2fc" stroke-width="8" stroke-dasharray="180 250" stroke-linecap="round" fill="none" class="animate-dash" />
                          <text x="50" y="55" text-anchor="middle" fill="#fff" font-size="16" font-weight="bold">94.8%</text>
                          <text x="50" y="70" text-anchor="middle" fill="#86909c" font-size="8">运行健康度</text>
                        </svg>
                      </div>
                    </div>
                    <div class="screen-card">
                      <div class="sc-title">网络流量实时趋势</div>
                      <div class="sc-chart line-chart">
                        <svg viewBox="0 0 100 50" class="line-svg">
                          <path d="M 0 40 Q 20 20, 40 35 T 80 15 T 100 10" fill="none" stroke="#8b5cf6" stroke-width="3" />
                          <path d="M 0 40 Q 20 20, 40 35 T 80 15 T 100 10 L 100 50 L 0 50 Z" fill="url(#blue-grad)" opacity="0.15" />
                          <defs>
                            <linearGradient id="blue-grad" x1="0" y1="0" x2="0" y2="1">
                              <stop offset="0%" stop-color="#8b5cf6" />
                              <stop offset="100%" stop-color="transparent" />
                            </linearGradient>
                          </defs>
                        </svg>
                      </div>
                    </div>
                  </div>

                  <!-- Center Map Visual -->
                  <div class="sg-col center-col">
                    <!-- Simulated SVG Cyber Map with Flylines -->
                    <div class="cyber-map-wrap">
                      <svg class="cyber-map-svg" viewBox="0 0 400 240">
                        <!-- Grid circles in background -->
                        <circle cx="200" cy="120" r="100" fill="none" stroke="#2563eb" stroke-dasharray="4 6" opacity="0.2" class="spin-clockwise" />
                        <circle cx="200" cy="120" r="70" fill="none" stroke="#ec4899" stroke-dasharray="2 4" opacity="0.15" class="spin-counter-clockwise" />
                        
                        <!-- Map outlines simulated -->
                        <path d="M 120 70 L 160 50 L 220 60 L 250 40 L 280 80 L 320 100 L 290 140 L 270 180 L 210 190 L 170 170 L 130 150 L 110 110 Z" fill="rgba(37, 99, 235, 0.05)" stroke="rgba(37, 99, 235, 0.2)" stroke-width="2" />
                        
                        <!-- Map Nodes -->
                        <g class="map-node" transform="translate(160, 90)">
                          <circle r="6" fill="#00f5ff" />
                          <circle r="12" fill="none" stroke="#00f5ff" stroke-width="1.5" class="ping-wave" />
                        </g>
                        <g class="map-node" transform="translate(240, 80)">
                          <circle r="6" fill="#ec4899" />
                          <circle r="12" fill="none" stroke="#ec4899" stroke-width="1.5" class="ping-wave-delay" />
                        </g>
                        <g class="map-node" transform="translate(280, 130)">
                          <circle r="6" fill="#00f5ff" />
                          <circle r="12" fill="none" stroke="#00f5ff" stroke-width="1.5" class="ping-wave" />
                        </g>
                        <g class="map-node" transform="translate(200, 140)">
                          <circle r="8" fill="#ffb800" />
                          <circle r="20" fill="none" stroke="#ffb800" stroke-width="2" class="ping-wave" />
                        </g>

                        <!-- Connecting Dynamic Flylines -->
                        <path d="M 160 90 Q 180 110 200 140" fill="none" stroke="#00f5ff" stroke-width="1.5" stroke-dasharray="5 5" class="flyline" />
                        <path d="M 240 80 Q 220 110 200 140" fill="none" stroke="#ec4899" stroke-width="1.5" stroke-dasharray="5 5" class="flyline-2" />
                        <path d="M 280 130 Q 240 135 200 140" fill="none" stroke="#00f5ff" stroke-width="1.5" stroke-dasharray="5 5" class="flyline" />
                      </svg>
                      
                      <div class="map-overlay-card">
                        <div class="card-row">
                          <span class="label">当前活动节点:</span>
                          <span class="val text-cyan">4 个区段</span>
                        </div>
                        <div class="card-row">
                          <span class="label">告警率:</span>
                          <span class="val text-pink">0.02%</span>
                        </div>
                      </div>
                    </div>
                  </div>

                  <!-- Right Charts -->
                  <div class="sg-col side-col">
                    <div class="screen-card">
                      <div class="sc-title">资源使用占比</div>
                      <div class="sc-chart bar-chart">
                        <div class="bar-row">
                          <div class="bar-label">CPU</div>
                          <div class="bar-track"><div class="bar-fill purple-fill" style="width: 74%;"></div></div>
                          <div class="bar-value">74%</div>
                        </div>
                        <div class="bar-row">
                          <div class="bar-label">内存</div>
                          <div class="bar-track"><div class="bar-fill blue-fill" style="width: 58%;"></div></div>
                          <div class="bar-value">58%</div>
                        </div>
                        <div class="bar-row">
                          <div class="bar-label">存储</div>
                          <div class="bar-track"><div class="bar-fill cyan-fill" style="width: 42%;"></div></div>
                          <div class="bar-value">42%</div>
                        </div>
                      </div>
                    </div>
                    <div class="screen-card">
                      <div class="sc-title">设备报警分类</div>
                      <div class="sc-chart progress-circles">
                        <div class="circle-item">
                          <div class="c-num text-red">3</div>
                          <div class="c-txt">严重</div>
                        </div>
                        <div class="circle-item">
                          <div class="c-num text-orange">8</div>
                          <div class="c-txt">一般</div>
                        </div>
                        <div class="circle-item">
                          <div class="c-num text-green">148</div>
                          <div class="c-txt">正常</div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Floating Interactive Elements -->
              <!-- Multiplayer Cursors -->
              <div class="mock-cursor cursor-chloe">
                <svg viewBox="0 0 24 24" class="cursor-arrow">
                  <path d="M 0 0 L 16 16 L 9 17 L 0 24 Z" fill="#2563eb" />
                </svg>
                <span class="cursor-tag chloe-tag">Chloe (UI设计师)</span>
              </div>

              <div class="mock-cursor cursor-jane">
                <svg viewBox="0 0 24 24" class="cursor-arrow">
                  <path d="M 0 0 L 16 16 L 9 17 L 0 24 Z" fill="#ec4899" />
                </svg>
                <span class="cursor-tag jane-tag">Jane (前端研发)</span>
              </div>

              <!-- AI Copilot Assistant Widget -->
              <div class="floating-panel ai-panel animate-float">
                <div class="panel-header">
                  <icon-message /> <span>AI 智能大屏设计助手</span>
                </div>
                <div class="panel-body">
                  <div class="ai-chat">
                    <div class="ai-msg user">
                      生成一个深色调的全国物流监控中心大屏，带流光效果
                    </div>
                    <div class="ai-msg assistant typing">
                      已为您设计蓝紫色调，包含中心节点、网络链路流光图及3个关键指标占比柱状图...
                    </div>
                  </div>
                  <div class="ai-action">
                    <a-button type="primary" size="mini" shape="round" status="success">一键应用到画布</a-button>
                  </div>
                </div>
              </div>

              <!-- Telemetry JSON Data Stream Widget -->
              <div class="floating-panel data-panel animate-float-delayed">
                <div class="panel-header">
                  <icon-storage /> <span>实时 WebSocket 数据源</span>
                </div>
                <div class="panel-body font-mono">
                  <div class="code-line"><span class="c-key">"timestamp"</span>: <span class="c-val">1718092800</span>,</div>
                  <div class="code-line"><span class="c-key">"nodeId"</span>: <span class="c-val">"BJ-03"</span>,</div>
                  <div class="code-line"><span class="c-key">"activeConnections"</span>: <span class="c-num">8421</span>,</div>
                  <div class="code-line"><span class="c-key">"status"</span>: <span class="c-str">"online"</span></div>
                  <div class="data-ping-wrapper">
                    <span class="ping-dot"></span>
                    <span class="ping-text">数据刷新中 (每秒 10 条)</span>
                  </div>
                </div>
              </div>
            </div>
          </main>

          <!-- Right panel: Properties -->
          <aside class="editor-right-panel">
            <div class="panel-section-title">组件属性</div>
            <div class="prop-list">
              <div class="prop-group">
                <label class="prop-label">底图样式</label>
                <div class="prop-input-wrap">
                  <a-select defaultValue="dark-cyber" size="mini" class="mini-select">
                    <a-option value="dark-cyber">科技深蓝</a-option>
                    <a-option value="light-clean">极简明亮</a-option>
                    <a-option value="3d-globe">3D三维地球</a-option>
                  </a-select>
                </div>
              </div>
              <div class="prop-group">
                <label class="prop-label">背景发光 (Glow)</label>
                <div class="prop-input-wrap">
                  <a-slider :defaultValue="75" :max="100" class="mini-slider" />
                </div>
              </div>
              <div class="prop-group">
                <label class="prop-label">飞线速度 (fps)</label>
                <div class="prop-input-wrap">
                  <a-slider :defaultValue="60" :max="120" class="mini-slider" />
                </div>
              </div>
              <div class="prop-group">
                <label class="prop-label">透明度</label>
                <div class="prop-input-wrap">
                  <a-slider :defaultValue="85" :max="100" class="mini-slider" />
                </div>
              </div>
            </div>
          </aside>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { useFrontUserStore } from '../../../store/frontUser'
import { ElMessage } from 'element-plus'

const frontUserStore = useFrontUserStore()

function goToConsole() {
  if (frontUserStore.frontToken) {
    ElMessage.success('预览分享链接已成功复制到剪贴板！')
  } else {
    frontUserStore.showLogin()
  }
}
</script>

<style scoped>
.mockup-section {
  max-width: 1280px;
  margin: 0 auto;
  padding: 60px 24px;
  position: relative;
  z-index: 10;
}

.section-header {
  text-align: center;
  margin-bottom: 48px;
}

.section-tag {
  font-size: 12px;
  font-weight: 700;
  color: #4f46e5;
  text-transform: uppercase;
  letter-spacing: 1.5px;
  background-color: rgba(79, 70, 229, 0.08);
  padding: 4px 10px;
  border-radius: 4px;
}

.section-header h2 {
  font-size: 32px;
  font-weight: 800;
  color: #1f2937;
  margin: 16px 0 12px 0;
  letter-spacing: -0.5px;
}

.section-header p {
  font-size: 16px;
  color: #4e5969;
  max-width: 600px;
  margin: 0 auto;
}

.editor-mockup-wrapper {
  background: radial-gradient(100% 100% at 50% 0%, rgba(99, 102, 241, 0.04) 0%, transparent 60%);
  padding: 16px;
  border-radius: 20px;
  border: 1px solid rgba(229, 230, 235, 0.8);
  background-color: rgba(255, 255, 255, 0.6);
  backdrop-filter: blur(8px);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.04);
}

.editor-window {
  width: 100%;
  height: 600px;
  background-color: #0d111a;
  border-radius: 12px;
  border: 1px solid #1f293d;
  box-shadow: 0 30px 60px rgba(0, 0, 0, 0.25);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.window-titlebar {
  height: 44px;
  background-color: #0b0f17;
  border-bottom: 1px solid #1e2638;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 16px;
  user-select: none;
}

.window-dots {
  display: flex;
  gap: 8px;
}

.window-dots .dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  display: inline-block;
}

.window-dots .dot.red { background-color: #ff5f56; }
.window-dots .dot.yellow { background-color: #ffbd2e; }
.window-dots .dot.green { background-color: #27c93f; }

.window-title {
  color: #8f9cae;
  font-size: 12px;
  font-weight: 500;
}

.window-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.share-mini-btn {
  background-color: #1e293b;
  color: #fff;
  border: 1px solid #334155;
  border-radius: 6px;
  padding: 4px 10px;
  font-size: 11px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 4px;
  font-weight: 600;
  transition: all 0.2s;
}

.share-mini-btn:hover {
  background-color: #2563eb;
  border-color: #3b82f6;
}

.editor-body {
  flex: 1;
  display: flex;
  overflow: hidden;
}

.editor-left-panel, .editor-right-panel {
  width: 180px;
  background-color: #0b0e14;
  border-right: 1px solid #191f2e;
  display: flex;
  flex-direction: column;
  padding: 16px 12px;
  box-sizing: border-box;
}

.editor-right-panel {
  border-right: none;
  border-left: 1px solid #191f2e;
}

.panel-section-title {
  font-size: 11px;
  color: #4b5563;
  text-transform: uppercase;
  font-weight: 700;
  margin-bottom: 12px;
  letter-spacing: 0.5px;
}

.widget-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.widget-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  color: #94a3b8;
  border-radius: 8px;
  cursor: pointer;
  font-size: 13px;
  font-weight: 500;
  transition: all 0.2s;
}

.widget-item:hover {
  background-color: rgba(255, 255, 255, 0.03);
  color: #f8fafc;
}

.widget-item.active {
  background-color: rgba(37, 99, 235, 0.15);
  color: #3b82f6;
  border: 1px solid rgba(37, 99, 235, 0.3);
}

.w-icon {
  font-size: 16px;
}

.prop-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.prop-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.prop-label {
  font-size: 11px;
  color: #64748b;
  font-weight: 500;
}

.mini-select {
  width: 100%;
  background-color: #111827 !important;
  border: 1px solid #1e293b !important;
  color: #cbd5e1 !important;
}

.mini-slider {
  margin: 4px 0 !important;
}

.editor-canvas-container {
  flex: 1;
  background-color: #080a0f;
  position: relative;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
}

.canvas-ruler {
  position: absolute;
  background-color: #1e293b;
  opacity: 0.3;
}

.canvas-ruler.horizontal {
  top: 0;
  left: 0;
  width: 100%;
  height: 1px;
}

.canvas-ruler.vertical {
  top: 0;
  left: 0;
  width: 1px;
  height: 100%;
}

.editor-canvas {
  width: 90%;
  height: 85%;
  background-color: #0b0f19;
  border: 1px solid #1e293b;
  border-radius: 8px;
  position: relative;
  overflow: hidden;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
  display: flex;
  flex-direction: column;
}

.canvas-grid-bg {
  position: absolute;
  inset: 0;
  background-image: linear-gradient(rgba(255, 255, 255, 0.02) 1px, transparent 1px),
                    linear-gradient(90deg, rgba(255, 255, 255, 0.02) 1px, transparent 1px);
  background-size: 16px 16px;
  pointer-events: none;
  z-index: 1;
}

.screen-layout {
  position: relative;
  z-index: 5;
  width: 100%;
  height: 100%;
  padding: 16px;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
}

.screen-header {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  margin-bottom: 12px;
}

.sh-title {
  color: #38bdf8;
  font-size: 15px;
  font-weight: 800;
  letter-spacing: 2px;
  text-shadow: 0 0 8px rgba(56, 189, 248, 0.5);
}

.sh-line {
  flex: 1;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(56, 189, 248, 0.5), transparent);
}

.screen-grid {
  flex: 1;
  display: flex;
  gap: 12px;
}

.sg-col {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.sg-col.side-col {
  width: 110px;
}

.sg-col.center-col {
  flex: 1;
  border: 1px solid rgba(56, 189, 248, 0.15);
  background-color: rgba(15, 23, 42, 0.6);
  border-radius: 6px;
  position: relative;
  overflow: hidden;
}

.screen-card {
  background-color: rgba(15, 23, 42, 0.75);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 6px;
  padding: 8px;
  display: flex;
  flex-direction: column;
  gap: 6px;
  flex: 1;
}

.sc-title {
  font-size: 9px;
  color: #64748b;
  font-weight: 700;
  border-left: 2px solid #38bdf8;
  padding-left: 4px;
}

.sc-chart {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.cyber-map-wrap {
  width: 100%;
  height: 100%;
  position: relative;
}

.cyber-map-svg {
  width: 100%;
  height: 100%;
}

.spin-clockwise {
  transform-origin: 200px 120px;
  animation: rotation-cw 20s linear infinite;
}

.spin-counter-clockwise {
  transform-origin: 200px 120px;
  animation: rotation-ccw 15s linear infinite;
}

@keyframes rotation-cw {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

@keyframes rotation-ccw {
  from { transform: rotate(360deg); }
  to { transform: rotate(0deg); }
}

.ping-wave {
  animation: ping-ring 2s cubic-bezier(0, 0, 0.2, 1) infinite;
  transform-origin: center;
}

.ping-wave-delay {
  animation: ping-ring 2s cubic-bezier(0, 0, 0.2, 1) 1s infinite;
  transform-origin: center;
}

@keyframes ping-ring {
  0% { r: 6px; opacity: 1; stroke-width: 2px; }
  100% { r: 24px; opacity: 0; stroke-width: 0.5px; }
}

.flyline {
  stroke-dasharray: 6 120;
  animation: dash-fly 3s linear infinite;
  stroke-linecap: round;
}

.flyline-2 {
  stroke-dasharray: 6 120;
  animation: dash-fly 3s linear 1.5s infinite;
  stroke-linecap: round;
}

@keyframes dash-fly {
  0% { stroke-dashoffset: 126; }
  100% { stroke-dashoffset: -126; }
}

.map-overlay-card {
  position: absolute;
  bottom: 8px;
  left: 8px;
  background-color: rgba(11, 15, 23, 0.85);
  border: 1px solid rgba(56, 189, 248, 0.2);
  border-radius: 4px;
  padding: 6px 10px;
  display: flex;
  flex-direction: column;
  gap: 2px;
  z-index: 10;
  backdrop-filter: blur(4px);
}

.card-row {
  display: flex;
  gap: 8px;
  font-size: 8px;
}

.card-row .label { color: #64748b; }
.card-row .val { font-weight: 700; }
.text-cyan { color: #22d3ee; }
.text-pink { color: #f472b6; }

.gauge-svg {
  width: 50px;
  height: 50px;
}

.animate-dash {
  transform: rotate(-90deg);
  transform-origin: 50px 50px;
}

.line-svg {
  width: 100%;
  height: 36px;
}

.bar-chart {
  display: flex;
  flex-direction: column;
  gap: 6px;
  justify-content: center;
}

.bar-row {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 8px;
}

.bar-label {
  width: 20px;
  color: #94a3b8;
}

.bar-track {
  flex: 1;
  height: 4px;
  background-color: #1e293b;
  border-radius: 2px;
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  border-radius: 2px;
}

.bar-fill.purple-fill { background: linear-gradient(90deg, #8b5cf6, #d946ef); }
.bar-fill.blue-fill { background: linear-gradient(90deg, #3b82f6, #06b6d4); }
.bar-fill.cyan-fill { background: linear-gradient(90deg, #0d9488, #10b981); }

.bar-value {
  width: 18px;
  color: #f1f5f9;
  text-align: right;
}

.progress-circles {
  display: flex;
  justify-content: space-around;
}

.circle-item {
  text-align: center;
}

.c-num {
  font-size: 13px;
  font-weight: 800;
}

.c-txt {
  font-size: 8px;
  color: #64748b;
}

.text-red { color: #ef4444; }
.text-orange { color: #f97316; }
.text-green { color: #10b981; }

.mock-cursor {
  position: absolute;
  z-index: 50;
  display: flex;
  flex-direction: column;
  pointer-events: none;
}

.cursor-arrow {
  width: 16px;
  height: 16px;
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.4));
}

.cursor-tag {
  margin-top: 4px;
  font-size: 9px;
  color: #fff;
  padding: 2px 6px;
  border-radius: 3px;
  font-weight: 600;
  white-space: nowrap;
  box-shadow: 0 4px 8px rgba(0,0,0,0.3);
}

.chloe-tag { background-color: #2563eb; }
.jane-tag { background-color: #ec4899; }

.cursor-chloe {
  top: 130px;
  left: 210px;
  animation: float-chloe 12s infinite alternate ease-in-out;
}

.cursor-jane {
  bottom: 80px;
  right: 140px;
  animation: float-jane 16s infinite alternate ease-in-out;
}

@keyframes float-chloe {
  0% { transform: translate(0, 0); }
  30% { transform: translate(120px, 40px); }
  60% { transform: translate(50px, -60px); }
  100% { transform: translate(-30px, 80px); }
}

@keyframes float-jane {
  0% { transform: translate(0, 0); }
  40% { transform: translate(-140px, -80px); }
  70% { transform: translate(-20px, 20px); }
  100% { transform: translate(-100px, -40px); }
}

.floating-panel {
  position: absolute;
  z-index: 40;
  background-color: rgba(13, 17, 26, 0.85);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 8px;
  width: 160px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.4);
  backdrop-filter: blur(8px);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.ai-panel {
  top: 40px;
  left: 10px;
}

.data-panel {
  bottom: 30px;
  right: 10px;
  width: 170px;
}

.panel-header {
  background-color: rgba(255, 255, 255, 0.03);
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
  padding: 6px 10px;
  font-size: 9px;
  font-weight: 700;
  color: #94a3b8;
  display: flex;
  align-items: center;
  gap: 6px;
}

.panel-body {
  padding: 8px;
}

.ai-chat {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-bottom: 8px;
}

.ai-msg {
  font-size: 8px;
  line-height: 1.4;
  padding: 4px 6px;
  border-radius: 4px;
}

.ai-msg.user {
  background-color: #1e293b;
  color: #cbd5e1;
  align-self: flex-start;
}

.ai-msg.assistant {
  background-color: rgba(79, 70, 229, 0.2);
  border: 1px solid rgba(79, 70, 229, 0.3);
  color: #c7d2fe;
  align-self: flex-end;
}

.typing::after {
  content: ' |';
  animation: blink-caret 0.8s infinite;
}

@keyframes blink-caret {
  50% { opacity: 0; }
}

.ai-action {
  display: flex;
  justify-content: flex-end;
}

.font-mono {
  font-family: Menlo, Monaco, Consolas, "Courier New", monospace;
  font-size: 7.5px;
  color: #38bdf8;
  line-height: 1.4;
}

.c-key { color: #a5b4fc; }
.c-val { color: #38bdf8; }
.c-num { color: #f472b6; }
.c-str { color: #34d399; }

.data-ping-wrapper {
  margin-top: 8px;
  display: flex;
  align-items: center;
  gap: 6px;
  border-top: 1px solid rgba(255,255,255,0.05);
  padding-top: 6px;
}

.ping-dot {
  width: 5px;
  height: 5px;
  background-color: #22c55e;
  border-radius: 50%;
  animation: ping-pulse 1s cubic-bezier(0, 0, 0.2, 1) infinite;
}

.ping-text {
  color: #64748b;
  font-size: 7px;
}

@keyframes ping-pulse {
  50% { opacity: 0.3; transform: scale(1.2); }
}

.animate-float {
  animation: floating-widget 6s ease-in-out infinite alternate;
}

.animate-float-delayed {
  animation: floating-widget 7s ease-in-out 1s infinite alternate;
}

@keyframes floating-widget {
  0% { transform: translateY(0); }
  100% { transform: translateY(-10px); }
}

@media (max-width: 992px) {
  .editor-mockup-wrapper { display: none; }
}
</style>
