<template>
  <div class="min-h-screen">
    <div class="fixed inset-0 pointer-events-none overflow-hidden">
      <div class="absolute -top-40 -left-40 w-96 h-96 bg-violet-900/20 rounded-full blur-3xl"></div>
      <div class="absolute -bottom-40 -right-40 w-96 h-96 bg-emerald-900/10 rounded-full blur-3xl"></div>
    </div>

    <header class="relative z-10 border-b border-chord-border">
      <div class="max-w-6xl mx-auto px-4 sm:px-6 h-14 sm:h-16 flex items-center justify-between">
        <RouterLink to="/" class="flex items-center gap-2 sm:gap-3 group">
          <div class="w-7 h-7 sm:w-8 sm:h-8 bg-chord-accent rounded-lg flex items-center
                      justify-center group-hover:bg-violet-500 transition-colors shrink-0">
            <svg class="w-3.5 h-3.5 sm:w-4 sm:h-4 text-white" fill="currentColor" viewBox="0 0 24 24">
              <path d="M12 3v10.55c-.59-.34-1.27-.55-2-.55-2.21 0-4 1.79-4 4s1.79 4 4 4 4-1.79 4-4V7h4V3h-6z"/>
            </svg>
          </div>
          <span class="font-display font-bold text-base sm:text-lg tracking-tight">AudioChord</span>
        </RouterLink>

        <nav class="flex items-center gap-4 sm:gap-6">
          <RouterLink to="/history"
            class="label hover:text-chord-text transition-colors text-xs sm:text-xs"
            active-class="text-chord-text">
            History
          </RouterLink>
          <span class="label text-xs hidden sm:inline">v0.4.0</span>
        </nav>
      </div>
    </header>

    <main class="relative z-10">
      <RouterView />
    </main>
  </div>
</template>
