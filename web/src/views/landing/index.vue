<template>
  <div class="landing-container">
    <!-- Ambient Background Glows -->
    <div class="ambient-glow glow-1"></div>
    <div class="ambient-glow glow-2"></div>
    <div class="ambient-glow glow-3"></div>

    <!-- Page Components -->
    <LandingHeader />
    <HeroSection />
    <EditorMockup />
    <FeatureGrid />
    <TemplateGallery />
    <ActionBlock />
    <LandingFooter />
  </div>
</template>

<script setup lang="ts">
import LandingHeader from './components/LandingHeader.vue'
import HeroSection from './components/HeroSection.vue'
import EditorMockup from './components/EditorMockup.vue'
import FeatureGrid from './components/FeatureGrid.vue'
import TemplateGallery from './components/TemplateGallery.vue'
import ActionBlock from './components/ActionBlock.vue'
import LandingFooter from './components/LandingFooter.vue'
</script>

<style scoped>
/* Main Container: must scroll, handles its own viewport scroll */
.landing-container {
  height: 100vh;
  width: 100vw;
  overflow-y: auto;
  overflow-x: hidden;
  background-color: #ffffff;
  color: #1d2129;
  font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  position: relative;
  scroll-behavior: smooth;
}

/* Ambient Radial Glows */
.ambient-glow {
  position: absolute;
  border-radius: 50%;
  filter: blur(120px);
  z-index: 0;
  pointer-events: none;
}

.glow-1 {
  width: 600px;
  height: 600px;
  background: radial-gradient(circle, rgba(99, 102, 241, 0.15) 0%, transparent 70%);
  top: -100px;
  right: -50px;
}

.glow-2 {
  width: 500px;
  height: 500px;
  background: radial-gradient(circle, rgba(236, 72, 153, 0.12) 0%, transparent 70%);
  top: 150px;
  left: -100px;
}

.glow-3 {
  width: 700px;
  height: 700px;
  background: radial-gradient(circle, rgba(14, 165, 233, 0.1) 0%, transparent 70%);
  bottom: 10%;
  right: 10%;
}
</style>
