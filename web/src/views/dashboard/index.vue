<template>
  <div class="dashboard-container">
    <!-- Welcome banner matching reference aesthetics -->
    <a-card class="welcome-card" :bordered="false">
      <div class="welcome-box">
        <a-avatar :size="64" :src="userStore.avatar || defaultAvatar" class="welcome-avatar" />
        <div class="welcome-text">
          <h3>欢迎回来，{{ userStore.username }}！</h3>
          <p>{{ userStore.introduction || settings.welcomeMessage }}</p>
        </div>
      </div>
    </a-card>

    <!-- Stats Grid -->
    <a-row :gutter="20" class="stats-row">
      <a-col :xs="24" :sm="12" :md="6" v-for="(stat, index) in stats" :key="index">
        <div class="stat-card">
          <div class="stat-card-left">
            <div class="stat-card-label">{{ stat.title }}</div>
            <div class="stat-card-value">{{ stat.value }}</div>
            <div class="stat-card-trend">
              较昨日 <span :class="parseFloat(stat.trend) >= 0 ? 'up' : 'down'">
                {{ parseFloat(stat.trend) >= 0 ? '+' : '' }}{{ stat.trend }}%
              </span>
            </div>
          </div>
          <div :style="{ backgroundColor: stat.bgColor }" class="stat-card-icon-wrap">
            <component :is="stat.icon" :style="{ color: stat.color, fontSize: '24px' }"></component>
          </div>
        </div>
      </a-col>
    </a-row>

    <!-- Main Content Area -->
    <a-row :gutter="20" class="content-row">
      <a-col :xs="24" :lg="16">
        <a-card title="项目概览" class="info-card" :bordered="false">
          <div class="project-info">
            <p><strong>迅捷后台管理系统模板</strong> 采用现代化技术栈开发：</p>
            <ul>
              <li><strong>后端：</strong> FastAPI + SQLAlchemy (Async) + Pydantic v2</li>
              <li><strong>前端：</strong> Vue 3 + TypeScript + Vite + Pinia + Vue Router + Arco Design</li>
              <li><strong>管理：</strong> Git 统一版本控制仓</li>
            </ul>
            <p class="desc">
              该模板提供了极佳的开发体验与高性能基础。你可以直接在 `app/api` 下编写后端业务逻辑，在 `web/src/views` 下扩展前端页面。
            </p>
          </div>
        </a-card>
      </a-col>
      <a-col :xs="24" :lg="8">
        <a-card title="快捷链接" class="shortcut-card" :bordered="false">
          <div class="shortcut-list">
            <a href="http://127.0.0.1:8000/docs" target="_blank" class="shortcut-item">
              <IconBook class="shortcut-icon" />
              <span>Swagger API 文档</span>
            </a>
            <a href="https://fastapi.tiangolo.com/" target="_blank" class="shortcut-item">
              <IconLink class="shortcut-icon" />
              <span>FastAPI 官方文档</span>
            </a>
            <a href="https://cn.vuejs.org/" target="_blank" class="shortcut-item">
              <IconLink class="shortcut-icon" />
              <span>Vue 3 官方文档</span>
            </a>
          </div>
        </a-card>
      </a-col>
    </a-row>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useUserStore } from '../../store/user'
import { IconDesktop, IconUser, IconFile, IconApps, IconBook, IconLink } from '@arco-design/web-vue/es/icon'
import { settings } from '../../config/settings'

const userStore = useUserStore()
const defaultAvatar = 'https://wpimg.wallstcn.com/f778738c-e4f8-4870-b634-56703b4acafe.gif'

const stats = ref([
  {
    title: '系统访问量',
    value: '12,543',
    icon: IconDesktop,
    trend: '12',
    color: '#165DFF',
    bgColor: '#E8F1FF'
  },
  {
    title: '在线设备',
    value: '1,240',
    icon: IconUser,
    trend: '5',
    color: '#00B42A',
    bgColor: '#E8FFE6'
  },
  {
    title: '待处理报警',
    value: '18',
    icon: IconFile,
    trend: '-8',
    color: '#F53F3F',
    bgColor: '#FFE8E8'
  },
  {
    title: '待更新软件',
    value: '3',
    icon: IconApps,
    trend: '0',
    color: '#FF7D00',
    bgColor: '#FFF3E8'
  }
])
</script>

<style scoped>
.dashboard-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.welcome-card {
  background: linear-gradient(135deg, #E8F1FF 0%, #E8EAFF 100%);
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.welcome-box {
  display: flex;
  align-items: center;
  gap: 20px;
}

.welcome-avatar {
  border: 4px solid #ffffff;
  box-shadow: 0 4px 10px rgba(22, 93, 255, 0.15);
}

.welcome-text h3 {
  margin: 0 0 6px 0;
  font-size: 20px;
  color: #1D2129;
}

.welcome-text p {
  margin: 0;
  font-size: 14px;
  color: #4E5969;
}

.stats-row {
  margin-top: 10px;
}

/* Dashboard Stat Cards matching reference */
.stat-card {
  background: #FFFFFF;
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  padding: 20px;
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  height: 100%;
  border: 1px solid #E5E6EB;
}

.stat-card-left {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.stat-card-label {
  font-size: 14px;
  color: #86909C;
}

.stat-card-value {
  font-size: 32px;
  font-weight: 700;
  color: #1D2129;
  line-height: 1.2;
}

.stat-card-trend {
  font-size: 12px;
  margin-top: 8px;
  color: #86909C;
}

.stat-card-trend .up {
  color: #00B42A;
  font-weight: bold;
}

.stat-card-trend .down {
  color: #F53F3F;
  font-weight: bold;
}

.stat-card-icon-wrap {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.content-row {
  margin-top: 10px;
}

.info-card, .shortcut-card {
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  border: 1px solid #E5E6EB;
  background: #FFFFFF;
}

.project-info {
  line-height: 1.8;
  color: #4E5969;
}

.project-info ul {
  padding-left: 20px;
  margin: 10px 0;
}

.project-info li {
  margin-bottom: 6px;
}

.desc {
  font-size: 14px;
  color: #4E5969;
  background-color: #F7F8FA;
  padding: 12px;
  border-radius: 4px;
  border-left: 4px solid #165DFF;
}

.shortcut-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.shortcut-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px;
  border-radius: 4px;
  background-color: #F7F8FA;
  color: #4E5969;
  text-decoration: none;
  font-weight: 500;
  transition: all 0.2s ease;
  border: 1px solid #E5E6EB;
}

.shortcut-item:hover {
  background-color: #E8F1FF;
  color: #165DFF;
  border-color: #B3D4FF;
}

.shortcut-icon {
  font-size: 20px;
  color: #86909C;
}

.shortcut-item:hover .shortcut-icon {
  color: #165DFF;
}
</style>
