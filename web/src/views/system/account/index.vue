<template>
  <div class="account-container">
    <a-row :gutter="20">
      <!-- Left Profile Card -->
      <a-col :xs="24" :md="8">
        <a-card class="profile-card" :bordered="false">
          <div class="avatar-wrapper">
            <a-avatar :key="userInfo.avatar" :size="100" class="user-avatar" :image-url="userInfo.avatar">
              {{ userInfo.nickname?.slice(0, 1) || userInfo.username?.slice(0, 1) }}
            </a-avatar>
            <h3 class="user-nickname">{{ userInfo.nickname }}</h3>
            <p class="user-role-text">
              <a-tag v-for="role in userInfo.roles" :key="role" color="arcoblue" size="small">{{ role }}</a-tag>
            </p>
          </div>
          <a-divider />
          <div class="user-details">
            <div class="detail-item">
              <span class="detail-label">登录账号</span>
              <span class="detail-value">{{ userInfo.username }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">手机号码</span>
              <span class="detail-value">{{ userInfo.phonenumber || '-' }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">用户邮箱</span>
              <span class="detail-value">{{ userInfo.email || '-' }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">最后登录 IP</span>
              <span class="detail-value">{{ userInfo.login_ip || '-' }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">最后登录时间</span>
              <span class="detail-value">{{ userInfo.login_date ? formatDate(userInfo.login_date) : '-' }}</span>
            </div>
          </div>
        </a-card>
      </a-col>

      <!-- Right Tab Card -->
      <a-col :xs="24" :md="16">
        <a-card class="tabs-card" :bordered="false">
          <a-tabs default-active-key="1" type="line">
            <a-tab-pane key="1" title="基本资料">
              <a-form :model="profileForm" ref="profileFormRef" layout="vertical" @submit-success="submitProfile">
                <a-form-item field="nickname" label="用户昵称" :rules="[{ required: true, message: '用户昵称不能为空' }]">
                  <a-input v-model="profileForm.nickname" placeholder="请输入用户昵称" />
                </a-form-item>
                
                <a-form-item field="phonenumber" label="手机号码" :rules="[
                  { match: /^1[3-9]\d{9}$/, message: '请输入正确的手机号码格式' }
                ]">
                  <a-input v-model="profileForm.phonenumber" placeholder="请输入手机号码" />
                </a-form-item>

                <a-form-item field="email" label="用户邮箱" :rules="[
                  { type: 'email', message: '请输入正确的邮箱格式' }
                ]">
                  <a-input v-model="profileForm.email" placeholder="请输入用户邮箱" />
                </a-form-item>

                <a-form-item field="sex" label="性别">
                  <a-radio-group v-model="profileForm.sex">
                    <a-radio value="0">男</a-radio>
                    <a-radio value="1">女</a-radio>
                    <a-radio value="2">未知</a-radio>
                  </a-radio-group>
                </a-form-item>

                <a-form-item>
                  <a-button type="primary" html-type="submit" :loading="submitLoading">保存修改</a-button>
                </a-form-item>
              </a-form>
            </a-tab-pane>

            <a-tab-pane key="2" title="修改密码">
              <a-form :model="pwdForm" ref="pwdFormRef" layout="vertical" @submit-success="submitPassword">
                <a-form-item field="old_password" label="旧密码" :rules="[{ required: true, message: '旧密码不能为空' }]">
                  <a-input-password v-model="pwdForm.old_password" placeholder="请输入旧密码" />
                </a-form-item>

                <a-form-item field="new_password" label="新密码" :rules="[
                  { required: true, message: '新密码不能为空' },
                  { min: 6, message: '新密码不能少于6位' }
                ]">
                  <a-input-password v-model="pwdForm.new_password" placeholder="请输入新密码" />
                </a-form-item>

                <a-form-item field="confirm_password" label="确认新密码" :rules="[
                  { required: true, message: '确认新密码不能为空' },
                  { validator: validateConfirmPassword }
                ]">
                  <a-input-password v-model="pwdForm.confirm_password" placeholder="请再次输入新密码" />
                </a-form-item>

                <a-form-item>
                  <a-button type="primary" html-type="submit" :loading="pwdSubmitLoading">确认修改</a-button>
                </a-form-item>
              </a-form>
            </a-tab-pane>
          </a-tabs>
        </a-card>
      </a-col>
    </a-row>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { Message } from '@arco-design/web-vue'
import { getInfo } from '../../../api/auth'
import { updateUserProfile, updateUserPassword } from '../../../api/user'
import { useUserStore } from '../../../store/user'
import { formatDate } from '../../../utils'

const userStore = useUserStore()
const submitLoading = ref(false)
const pwdSubmitLoading = ref(false)

const userInfo = reactive<any>({
  username: '',
  nickname: '',
  roles: [],
  phonenumber: '',
  email: '',
  sex: '0',
  avatar: '',
  login_ip: '',
  login_date: ''
})

const profileForm = reactive({
  nickname: '',
  phonenumber: '',
  email: '',
  sex: '0'
})

const pwdForm = reactive({
  old_password: '',
  new_password: '',
  confirm_password: ''
})

async function fetchUserInfo() {
  try {
    const res: any = await getInfo()
    Object.assign(userInfo, res)
    Object.assign(profileForm, {
      nickname: res.nickname || '',
      phonenumber: res.phonenumber || '',
      email: res.email || '',
      sex: res.sex || '0'
    })
  } catch (err) {
    console.error('获取用户信息失败', err)
  }
}

async function submitProfile() {
  submitLoading.value = true
  try {
    await updateUserProfile(profileForm)
    Message.success('个人信息更新成功')
    // refresh store & UI
    await userStore.getInfo()
    await fetchUserInfo()
  } catch (err: any) {
    console.error(err)
  } finally {
    submitLoading.value = false
  }
}

function validateConfirmPassword(value: string | undefined, callback: (error?: string) => void) {
  if (value !== pwdForm.new_password) {
    callback('两次输入的密码不一致')
  } else {
    callback()
  }
}

async function submitPassword() {
  pwdSubmitLoading.value = true
  try {
    await updateUserPassword({
      old_password: pwdForm.old_password,
      new_password: pwdForm.new_password
    })
    Message.success('密码修改成功，请妥善保管新密码')
    // Reset form
    Object.assign(pwdForm, {
      old_password: '',
      new_password: '',
      confirm_password: ''
    })
  } catch (err: any) {
    console.error(err)
  } finally {
    pwdSubmitLoading.value = false
  }
}

onMounted(() => {
  fetchUserInfo()
})
</script>

<style scoped>
.account-container {
  padding: 10px;
}

.profile-card {
  border-radius: 8px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05);
  background: #ffffff;
  margin-bottom: 20px;
}

.avatar-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 10px 0 0 0;
}

.user-avatar {
  border: 4px solid #f2f3f5;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  background-color: #165dff;
  font-size: 32px;
  font-weight: bold;
}

.user-avatar :deep(.arco-avatar-image) {
  display: flex !important;
  width: 100% !important;
  height: 100% !important;
  align-items: center;
  justify-content: center;
}

.user-avatar :deep(img) {
  width: 100% !important;
  height: 100% !important;
  object-fit: cover !important;
  border-radius: 50% !important;
  display: block !important;
}



.user-nickname {
  margin-top: 16px;
  margin-bottom: 8px;
  font-size: 18px;
  font-weight: 600;
  color: #1d2129;
}

.user-role-text {
  margin: 0;
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
}

.user-details {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 14px;
}

.detail-label {
  color: #86909c;
}

.detail-value {
  color: #1d2129;
  font-weight: 500;
}

.tabs-card {
  border-radius: 8px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05);
  background: #ffffff;
  min-height: 480px;
}

:deep(.arco-tabs-nav-tab) {
  margin-bottom: 16px;
}
</style>
