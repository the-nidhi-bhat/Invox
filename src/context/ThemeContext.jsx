import React, { createContext, useContext, useState, useEffect, useCallback } from 'react'

const ThemeContext = createContext(null)

export function ThemeProvider({ children }) {
  const [theme, setTheme] = useState(() => {
    if (typeof window !== 'undefined') {
      const saved = localStorage.getItem('theme')
      if (saved === 'dark' || saved === 'light') return saved
      return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
    }
    return 'dark'
  })
  const [hasUserPreference, setHasUserPreference] = useState(() => {
    if (typeof window === 'undefined') return false
    const saved = localStorage.getItem('theme')
    return saved === 'dark' || saved === 'light'
  })

  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
    document.documentElement.setAttribute('data-theme', theme)
    if (hasUserPreference) {
      localStorage.setItem('theme', theme)
    } else {
      localStorage.removeItem('theme')
    }
  }, [theme, hasUserPreference])

  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
    const handleChange = (e) => {
      if (!hasUserPreference) {
        setTheme(e.matches ? 'dark' : 'light')
      }
    }
    mediaQuery.addEventListener('change', handleChange)
    return () => mediaQuery.removeEventListener('change', handleChange)
  }, [hasUserPreference])

  const updateTheme = useCallback((nextTheme) => {
    setHasUserPreference(true)
    setTheme(nextTheme)
  }, [])

  const toggleTheme = useCallback(() => {
    updateTheme(prev => prev === 'dark' ? 'light' : 'dark')
  }, [updateTheme])

  const value = {
    theme,
    setTheme: updateTheme,
    toggleTheme,
    mounted
  }

  return (
    <ThemeContext.Provider value={value}>
      {children}
    </ThemeContext.Provider>
  )
}

export function useTheme() {
  const context = useContext(ThemeContext)
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider')
  }
  return context
}