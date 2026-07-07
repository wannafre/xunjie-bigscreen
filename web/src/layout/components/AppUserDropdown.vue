<template>
  <a-dropdown trigger="click" @select="handleSelect">
    <div class="header-avatar-wrap">
      <a-avatar
        :key="userInfo.avatar"
        :size="34"
        class="user-avatar"
        :image-url="userInfo.avatar"
      >
        {{ avatarText }}
      </a-avatar>
      <div class="user-meta">
        <span class="user-name">{{ userInfo.username }}</span>
        <span class="user-role">管理员</span>
      </div>
      <IconDown class="down-icon" />
    </div>

    <template #content>
      <a-doption value="profile">
        <template #icon>
          <IconUser />
        </template>
        个人中心
      </a-doption>
      <a-doption value="logout" style="color: #f53f3f">
        <template #icon>
          <IconExport />
        </template>
        退出登录
      </a-doption>
    </template>
  </a-dropdown>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { IconDown, IconExport, IconUser } from '@arco-design/web-vue/es/icon'

const props = defineProps<{
  userInfo: {
    username?: string
    avatar?: string
  }
}>()

const emit = defineEmits<{
  (event: 'profile'): void
  (event: 'logout'): void
}>()

const avatarText = computed(() => {
  return props.userInfo.username?.slice(0, 1).toUpperCase() || 'U'
})

function handleSelect(value: string | number | Record<string, any> | undefined) {
  if (value === 'profile') emit('profile')
  if (value === 'logout') emit('logout')
}
</script>

<style scoped>
.header-avatar-wrap {
  min-width: 142px;
  height: 46px;
  padding: 5px 4px;
  display: flex;
  align-items: center;
  gap: 9px;
  cursor: pointer;
  border-radius: 12px;
  background: transparent;
  transition: color 0.2s ease, opacity 0.2s ease;
}

.header-avatar-wrap:hover {
  background: transparent;
  opacity: 0.88;
}

.user-avatar {
  background: linear-gradient(135deg, #2563eb, #38bdf8) !important;
  color: #ffffff;
  font-weight: 700;
  box-shadow: 0 8px 20px rgba(37, 99, 235, 0.24);
}

.header-avatar-wrap :deep(.arco-avatar-image) {
  display: flex !important;
  width: 100% !important;
  height: 100% !important;
  align-items: center;
  justify-content: center;
}

.header-avatar-wrap :deep(img) {
  width: 100% !important;
  height: 100% !important;
  object-fit: cover !important;
  border-radius: 50% !important;
  display: block !important;
}

.user-meta {
  display: flex;
  flex-direction: column;
  gap: 1px;
  min-width: 0;
}

.user-name {
  color: #0f172a;
  font-size: 13px;
  font-weight: 700;
  line-height: 18px;
  max-width: 74px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.user-role {
  color: #94a3b8;
  font-size: 11px;
  line-height: 14px;
}

.down-icon {
  margin-left: auto;
  font-size: 12px;
  color: #94a3b8;
}

@media (max-width: 960px) {
  .header-avatar-wrap {
    min-width: auto;
  }

  .user-meta,
  .down-icon {
    display: none;
  }
}
</style>


