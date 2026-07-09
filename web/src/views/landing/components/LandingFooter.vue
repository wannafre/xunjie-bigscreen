<template>
  <footer class="landing-footer">
    <div class="footer-bottom">
      <p>&copy; 2026 迅捷大屏. All Rights Reserved. 想法即大屏，设计即代码.</p>
      <div class="footer-links">
        <a href="#" class="f-link">服务条款</a>
        <a href="#" class="f-link">隐私政策</a>
        <a href="#" class="f-link">联系我们</a>
      </div>
    </div>
  </footer>
</template>

<script setup lang="ts">
// Footer component
</script>

<style scoped>
.landing-footer {
  background-color: #0b0f19;
  color: #4b5563;
  padding: 40px 24px;
  border-top: 1px solid #1f293d;
  font-size: 13px;
  position: relative;
  z-index: 10;
}

.footer-bottom {
  max-width: 1280px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 20px;
}

.footer-bottom p {
  margin: 0;
  color: #64748b;
}

.footer-links {
  display: flex;
  gap: 24px;
}

.f-link {
  color: #64748b;
  text-decoration: none;
  transition: color 0.2s;
}

.f-link:hover {
  color: #f1f5f9;
}

@media (max-width: 600px) {
  .footer-bottom { flex-direction: column; text-align: center; }
}
</style>
