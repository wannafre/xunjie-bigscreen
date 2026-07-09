<template>
  <section class="hero-section">
    <div class="capsule-badge">
      <span class="badge-dot"></span>
      <span class="badge-text">想法即大屏 · 设计即代码</span>
    </div>
    
    <h1 class="hero-title">
      智能可视化数据大屏<br />
      <span class="gradient-text">与产研协作设计平台</span>
    </h1>
    
    <p class="hero-subtitle">
      告别传统代码开发。一站式集成 AI 智能生成、三维 GIS 地图、动态组件库与多源数据联动。<br />
      从创意草图到大厅大屏交付，让您的数据瞬间释放价值。
    </p>

    <!-- Sub-Features / Badges -->
    <div class="hero-badges">
      <div class="badge-item">
        <icon-thunderbolt class="badge-icon purple" />
        <span>AI 智能大屏</span>
      </div>
      <div class="badge-item">
        <icon-compass class="badge-icon blue" />
        <span>三维三维场景</span>
      </div>
      <div class="badge-item">
        <icon-palette class="badge-icon pink" />
        <span>低代码拖拽</span>
      </div>
      <div class="badge-item">
        <icon-storage class="badge-icon green" />
        <span>实时数据源</span>
      </div>
    </div>

    <!-- Call to Actions -->
    <div class="cta-group">
      <button class="cta-btn primary-glow" @click="goToConsole">
        {{ frontUserStore.frontToken ? '进入设计控制台' : '免费开始使用' }}
      </button>
      <button class="cta-btn secondary-outline" @click="scrollToMockup">
        <icon-play-circle-fill class="btn-icon" />
        查看 AI 生成演示
      </button>
    </div>

    <div class="compatibility-info">
      支持 Windows、macOS、Linux、网页端及各种物理大屏拼接终端
    </div>
  </section>
</template>

<script setup lang="ts">
import { useFrontUserStore } from '../../../store/frontUser'
import { ElMessage } from 'element-plus'

const frontUserStore = useFrontUserStore()

function goToConsole() {
  if (frontUserStore.frontToken) {
    ElMessage.info('个人工作台正在拼命开发中，敬请期待！')
  } else {
    frontUserStore.showLogin()
  }
}

function scrollToMockup() {
  const mockupEl = document.getElementById('mockup')
  if (mockupEl) {
    mockupEl.scrollIntoView({ behavior: 'smooth' })
  }
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;800&display=swap');

.hero-section {
  max-width: 1280px;
  margin: 0 auto;
  padding: 80px 24px 60px 24px;
  text-align: center;
  position: relative;
  z-index: 10;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.capsule-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 6px 14px;
  background-color: rgba(79, 70, 229, 0.06);
  border: 1px solid rgba(79, 70, 229, 0.15);
  border-radius: 20px;
  margin-bottom: 24px;
}

.badge-dot {
  width: 6px;
  height: 6px;
  background-color: #4f46e5;
  border-radius: 50%;
  animation: pulse-glow 2s infinite;
}

.badge-text {
  font-size: 13px;
  font-weight: 600;
  color: #4f46e5;
  letter-spacing: 0.5px;
}

.hero-title {
  font-size: 54px;
  line-height: 1.15;
  font-weight: 800;
  letter-spacing: -1.5px;
  color: #1f2937;
  margin: 0 0 24px 0;
  font-family: 'Outfit', sans-serif;
}

.gradient-text {
  background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 40%, #db2777 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  display: inline-block;
}

.hero-subtitle {
  font-size: 18px;
  line-height: 1.6;
  color: #4e5969;
  max-width: 800px;
  margin: 0 0 40px 0;
}

.hero-badges {
  display: flex;
  gap: 16px;
  margin-bottom: 48px;
  flex-wrap: wrap;
  justify-content: center;
}

.badge-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 18px;
  background-color: #ffffff;
  border: 1px solid #e5e6eb;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 600;
  color: #1d2129;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.02);
  transition: all 0.3s;
}

.badge-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 18px rgba(0, 0, 0, 0.05);
  border-color: #cbd5e1;
}

.badge-icon {
  font-size: 16px;
}

.badge-icon.purple { color: #8b5cf6; }
.badge-icon.blue { color: #3b82f6; }
.badge-icon.pink { color: #ec4899; }
.badge-icon.green { color: #10b981; }

.cta-group {
  display: flex;
  gap: 20px;
  margin-bottom: 32px;
}

.cta-btn {
  padding: 16px 36px;
  border-radius: 30px;
  font-size: 16px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s;
  box-sizing: border-box;
}

.cta-btn.primary-glow {
  background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
  color: #fff;
  border: none;
  box-shadow: 0 6px 20px rgba(79, 70, 229, 0.3);
}

.cta-btn.primary-glow:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 24px rgba(79, 70, 229, 0.4);
}

.cta-btn.secondary-outline {
  background-color: #ffffff;
  color: #4e5969;
  border: 1px solid #cbd5e1;
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.cta-btn.secondary-outline:hover {
  background-color: #f8fafc;
  color: #1f2937;
  border-color: #94a3b8;
}

.btn-icon {
  font-size: 18px;
  color: #4f46e5;
}

.compatibility-info {
  font-size: 12px;
  color: #86909c;
}

@keyframes pulse-glow {
  0%, 100% { transform: scale(1); opacity: 1; box-shadow: 0 0 0 0 rgba(79, 70, 229, 0.4); }
  50% { transform: scale(1.15); opacity: 0.8; box-shadow: 0 0 8px 3px rgba(79, 70, 229, 0.2); }
}

@media (max-width: 992px) {
  .hero-title { font-size: 40px; }
}

@media (max-width: 600px) {
  .hero-title { font-size: 32px; }
  .hero-subtitle { font-size: 15px; }
  .cta-group { flex-direction: column; width: 100%; gap: 12px; }
  .cta-btn { width: 100%; text-align: center; }
}
</style>
