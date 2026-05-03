<template>
  <div class="min-h-screen">
    <div class="fixed inset-0 pointer-events-none overflow-hidden">
      <div class="absolute -top-40 -left-40 w-96 h-96 bg-violet-900/20 rounded-full blur-3xl"></div>
      <div class="absolute -bottom-40 -right-40 w-96 h-96 bg-emerald-900/10 rounded-full blur-3xl"></div>
    </div>

    <header class="relative z-10 border-b border-chord-border">
      <div class="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">
        <RouterLink to="/" class="flex items-center gap-3 group">
          <div class="w-8 h-8 bg-chord-accent rounded-lg flex items-center justify-center
                      group-hover:bg-violet-500 transition-colors">
            <svg class="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 24 24">
              <path d="M12 3v10.55c-.59-.34-1.27-.55-2-.55-2.21 0-4 1.79-4 4s1.79 4 4 4 4-1.79 4-4V7h4V3h-6z"/>
            </svg>
          </div>
          <span class="font-display font-bold text-lg tracking-tight">AudioChord</span>
        </RouterLink>

        <nav class="flex items-center gap-6">
          <RouterLink to="/history"
            class="label hover:text-chord-text transition-colors"
            active-class="text-chord-text">
            History
          </RouterLink>
          <span class="label">v0.2.0</span>
        </nav>
      </div>
    </header>

    <main class="relative z-10">
      <RouterView />
    </main>
  </div>
</template>
