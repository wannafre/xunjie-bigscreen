<template>
  <section id="features" class="features-section">
    <div class="section-header">
      <span class="section-tag">核心优势</span>
      <h2>不仅仅是编辑器，更是专业大屏生产力工具</h2>
      <p>我们打通了从视觉设计、组件拖拽、数据对接、到大屏多端适配与私有化部署的全链路</p>
    </div>

    <div class="feature-grid">
      <div class="feature-card">
        <div class="feat-icon-box bg-purple">
          <icon-thunderbolt />
        </div>
        <h3>AI 智能辅助创作</h3>
        <p>只需要输入一句话，AI 就可以直接帮您完成组件排版、大屏框架搭建、配色优化甚至生成虚拟仿真数据。</p>
      </div>
      <div class="feature-card">
        <div class="feat-icon-box bg-blue">
          <icon-compass />
        </div>
        <h3>三维 GIS 与地图可视化</h3>
        <p>支持快速上传 SVG、GeoJSON 或三维模型，一键生成区域热力、轨迹飞线、点位标记，完美适配城市大脑与物流图景。</p>
      </div>
      <div class="feature-card">
        <div class="feat-icon-box bg-pink">
          <icon-palette />
        </div>
        <h3>高精度低代码画板</h3>
        <p>参考线自动吸附、像素级拖拽定位、无限步历史撤销与恢复。专为大屏设计的多分辨率智能缩放适配（等比、拉伸、自适应）。</p>
      </div>
      <div class="feature-card">
        <div class="feat-icon-box bg-green">
          <icon-storage />
        </div>
        <h3>全协议动态数据源</h3>
        <p>内置支持 HTTP API、SQL 数据库直连、WebSocket 实时推送，以及各种 MQTT 物联网协议数据流，零延迟实时展示。</p>
      </div>
      <div class="feature-card">
        <div class="feat-icon-box bg-orange">
          <icon-user-group />
        </div>
        <h3>团队云端无缝协作</h3>
        <p>支持多人实时编辑同一块大屏，修改内容毫秒级同步。内置评论批注系统，打通设计、产品与开发人员沟通壁垒。</p>
      </div>
      <div class="feature-card">
        <div class="feat-icon-box bg-cyan">
          <icon-settings />
        </div>
        <h3>私有化部署与极速导出</h3>
        <p>支持一键生成静态包导出离线运行，也支持完整系统的本地私有化集群部署，确保企业内部敏感数据 100% 安全。</p>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
// Features grid component
</script>

<style scoped>
.features-section {
  max-width: 1280px;
  margin: 0 auto;
  padding: 80px 24px;
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

.feature-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 24px;
}

.feature-card {
  background-color: #ffffff;
  border: 1px solid #e5e6eb;
  border-radius: 16px;
  padding: 32px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.01);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}

.feature-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 20px 30px rgba(0, 0, 0, 0.05);
  border-color: #cbd5e1;
}

.feat-icon-box {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  margin-bottom: 20px;
}

.feat-icon-box.bg-purple { background-color: rgba(139, 92, 246, 0.1); color: #8b5cf6; }
.feat-icon-box.bg-blue { background-color: rgba(59, 130, 246, 0.1); color: #3b82f6; }
.feat-icon-box.bg-pink { background-color: rgba(236, 72, 153, 0.1); color: #ec4899; }
.feat-icon-box.bg-green { background-color: rgba(16, 185, 129, 0.1); color: #10b981; }
.feat-icon-box.bg-orange { background-color: rgba(249, 115, 22, 0.1); color: #f97316; }
.feat-icon-box.bg-cyan { background-color: rgba(6, 182, 212, 0.1); color: #06b6d4; }

.feature-card h3 {
  font-size: 18px;
  font-weight: 700;
  color: #1f2937;
  margin: 0 0 12px 0;
}

.feature-card p {
  font-size: 14px;
  line-height: 1.6;
  color: #4e5969;
  margin: 0;
}
</style>
