<template>
  <section class="action-block-section">
    <div class="action-content">
      <h2>开启您的大屏敏捷开发之旅</h2>
      <p>无论是大屏新手还是资深开发，迅捷大屏都将助您缩短 90% 的大屏交付周期。</p>
      <button class="action-start-btn" @click="goToConsole">立即免费体验</button>
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
</script>

<style scoped>
.action-block-section {
  background-color: #0f172a;
  background-image: radial-gradient(circle at 50% 0%, rgba(99, 102, 241, 0.15) 0%, transparent 60%),
                    linear-gradient(rgba(255, 255, 255, 0.01) 1px, transparent 1px),
                    linear-gradient(90deg, rgba(255, 255, 255, 0.01) 1px, transparent 1px);
  background-size: 100% 100%, 32px 32px, 32px 32px;
  padding: 100px 24px;
  text-align: center;
  color: #ffffff;
  position: relative;
  z-index: 10;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
}

.action-content {
  max-width: 650px;
  margin: 0 auto;
}

.action-block-section h2 {
  font-size: 36px;
  font-weight: 800;
  margin: 0 0 16px 0;
  letter-spacing: -1px;
}

.action-block-section p {
  font-size: 16px;
  color: #94a3b8;
  margin: 0 0 36px 0;
  line-height: 1.6;
}

.action-start-btn {
  background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
  color: #ffffff;
  border: none;
  padding: 16px 44px;
  border-radius: 30px;
  font-size: 16px;
  font-weight: 700;
  cursor: pointer;
  box-shadow: 0 10px 25px rgba(79, 70, 229, 0.35);
  transition: all 0.3s;
}

.action-start-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 14px 30px rgba(79, 70, 229, 0.5);
}
</style>
