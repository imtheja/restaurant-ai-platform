/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_BASE_URL: string
  readonly VITE_RESTAURANT_SERVICE_URL: string
  readonly VITE_MENU_SERVICE_URL: string
  readonly VITE_AI_SERVICE_URL: string
  readonly DEV: boolean
  readonly PROD: boolean
  readonly MODE: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}