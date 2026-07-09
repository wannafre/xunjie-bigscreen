<template>
  <section id="templates" class="templates-section">
    <div class="section-header">
      <span class="section-tag">模板市场</span>
      <h2>100+ 覆盖多行业的精美大屏模板</h2>
      <p>支持一键应用，修改内容即可发布，零设计基础也能搭建专业级大屏</p>
    </div>

    <div class="template-gallery">
      <div class="template-card-box">
        <div class="template-img bg-temp-1"></div>
        <div class="template-info">
          <h4>智慧交通应急指挥中心</h4>
          <span>支持多维分析与雷达扫描点</span>
        </div>
      </div>
      <div class="template-card-box">
        <div class="template-img bg-temp-2"></div>
        <div class="template-info">
          <h4>企业数字化物流追踪总览</h4>
          <span>集成全球航班飞线与港口热力</span>
        </div>
      </div>
      <div class="template-card-box">
        <div class="template-img bg-temp-3"></div>
        <div class="template-info">
          <h4>工业互联网数字孪生工厂</h4>
          <span>支持车间三维视角与设备故障警报</span>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
// Templates gallery component
</script>

<style scoped>
.templates-section {
  max-width: 1280px;
  margin: 0 auto;
  padding: 60px 24px 80px 24px;
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

.template-gallery {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 28px;
}

.template-card-box {
  background-color: #ffffff;
  border: 1px solid #e5e6eb;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.01);
  transition: all 0.3s;
  cursor: pointer;
}

.template-card-box:hover {
  transform: translateY(-4px);
  box-shadow: 0 20px 30px rgba(0, 0, 0, 0.06);
  border-color: #cbd5e1;
}

.template-img {
  width: 100%;
  height: 200px;
  background-size: cover;
  background-position: center;
}

.bg-temp-1 {
  background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%),
              radial-gradient(circle at 50% 50%, rgba(56, 189, 248, 0.3) 0%, transparent 60%);
  background-blend-mode: screen;
  position: relative;
}
.bg-temp-1::after {
  content: '⚡ Smart Traffic Hub';
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #38bdf8;
  font-weight: 700;
  font-size: 16px;
  text-shadow: 0 0 10px rgba(56, 189, 248, 0.5);
}

.bg-temp-2 {
  background: linear-gradient(135deg, #090d16 0%, #0d2a4a 100%),
              radial-gradient(circle at 30% 70%, rgba(236, 72, 153, 0.25) 0%, transparent 65%);
  background-blend-mode: screen;
  position: relative;
}
.bg-temp-2::after {
  content: '✈ Global Logistics Node';
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #f472b6;
  font-weight: 700;
  font-size: 16px;
  text-shadow: 0 0 10px rgba(236, 72, 153, 0.5);
}

.bg-temp-3 {
  background: linear-gradient(135deg, #030712 0%, #064e3b 100%),
              radial-gradient(circle at 80% 20%, rgba(16, 185, 129, 0.3) 0%, transparent 60%);
  background-blend-mode: screen;
  position: relative;
}
.bg-temp-3::after {
  content: '⚙ Digital Twin Factory';
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #34d399;
  font-weight: 700;
  font-size: 16px;
  text-shadow: 0 0 10px rgba(52, 211, 153, 0.5);
}

.template-info {
  padding: 20px;
}

.template-info h4 {
  font-size: 16px;
  font-weight: 700;
  color: #1f2937;
  margin: 0 0 6px 0;
}

.template-info span {
  font-size: 12px;
  color: #64748b;
}
</style>
