// src/content/ua.ts

export const content = {
  // Meta
  meta: {
    title: 'LabelCheck UA — Перевірка етикеток дієтичних добавок',
    description: 'Автоматична перевірка етикеток БАДів на відповідність законодавству України. Уникніть штрафів до 640 000 грн.',
  },

  // Header
  header: {
    logo: 'LabelCheck UA',
    nav: {
      howItWorks: 'Як це працює',
      pricing: 'Тарифи',
      checker: 'Перевірка',
      generator: 'Генератор',
      editor: 'Редактор',
    },
    cta: 'Перевірити етикетку',
  },

  // Hero Section
  hero: {
    badge: 'AI-перевірка за 20 секунд',
    title: 'Перевірте етикетку',
    titleHighlight: 'дієтичної добавки',
    subtitle: 'Автоматична перевірка на відповідність законодавству України. Уникніть штрафів до 640 000 грн за неправильне маркування.',
    primaryCta: 'Перевірити етикетку',
    secondaryCta: 'Як це працює',
    stats: {
      checks: '10,000+',
      checksLabel: 'перевірок',
      accuracy: '98%',
      accuracyLabel: 'точність',
      time: '20 сек',
      timeLabel: 'на перевірку',
    },
  },

  // How It Works
  howItWorks: {
    title: 'Як це працює',
    subtitle: 'Перевірка етикетки за три простих кроки',
    steps: [
      {
        number: '1',
        icon: 'Upload',
        title: 'Завантажте фото',
        description: 'Завантажте фото або скан етикетки вашої дієтичної добавки у форматі JPG, PNG або PDF.',
      },
      {
        number: '2',
        icon: 'Scan',
        title: 'AI-аналіз',
        description: 'Наша система розпізнає текст і перевіряє відповідність Закону №4122-IX, №2639-VIII та Наказу МОЗ №1114.',
      },
      {
        number: '3',
        icon: 'FileCheck',
        title: 'Отримайте звіт',
        description: 'Отримайте детальний звіт з помилками, попередженнями та рекомендаціями щодо виправлення.',
      },
    ],
  },

  // Features
  features: {
    title: 'Чому LabelCheck UA',
    subtitle: 'Комплексна перевірка всіх вимог законодавства',
    items: [
      {
        icon: 'Shield',
        title: 'Перевірка дозувань',
        description: 'Автоматична перевірка доз вітамінів та мінералів згідно з лімітами EFSA та Наказу МОЗ №1114.',
      },
      {
        icon: 'AlertTriangle',
        title: 'Заборонені фрази',
        description: 'Виявлення заборонених тверджень про лікування, діагностику та профілактику захворювань.',
      },
      {
        icon: 'FileText',
        title: "Обов'язкові поля",
        description: "Перевірка наявності всіх 18 обов'язкових елементів маркування згідно законодавства.",
      },
      {
        icon: 'Scale',
        title: 'Розрахунок штрафів',
        description: 'Автоматичний розрахунок потенційних штрафів за кожне порушення (до 640 000 грн).',
      },
      {
        icon: 'Clock',
        title: 'Швидкий результат',
        description: 'Повний аналіз етикетки за 15-20 секунд завдяки технології Claude AI.',
      },
      {
        icon: 'Download',
        title: 'PDF-звіт',
        description: 'Завантажте детальний звіт у PDF для внутрішнього використання або надання юристу.',
      },
    ],
  },

  // CTA Section
  cta: {
    title: 'Готові перевірити свою етикетку?',
    subtitle: 'Перша перевірка безкоштовно. Результат за 20 секунд.',
    button: 'Почати перевірку',
  },

  // Checker Page
  checker: {
    title: 'Перевірка етикетки',
    subtitle: 'Завантажте фото етикетки для аналізу',
    upload: {
      title: 'Перетягніть зображення сюди',
      subtitle: 'або натисніть для вибору',
      formats: 'Підтримуються формати: JPG, PNG, PDF (до 10 МБ)',
      button: 'Завантажити файл',
      dragActive: 'Відпустіть файл тут...',
    },
    progress: {
      step1: 'Розпізнавання тексту',
      step1Description: 'AI аналізує зображення та витягує інформацію',
      step2: 'Перевірка відповідності',
      step2Description: 'Порівняння з вимогами законодавства',
    },
    results: {
      title: 'Результати перевірки',
      valid: 'Етикетка відповідає вимогам',
      invalid: 'Виявлено порушення',
      errors: 'Критичні помилки',
      warnings: 'Попередження',
      correct: 'Відповідає вимогам',
      totalPenalty: 'Потенційний штраф',
      downloadPdf: 'Завантажити PDF',
      sendEmail: 'Надіслати на пошту',
      share: 'Поділитися',
      checkAnother: 'Перевірити іншу етикетку',
    },
    errors: {
      fileTooBig: 'Файл занадто великий. Максимальний розмір: 10 МБ',
      invalidFormat: 'Невірний формат. Підтримуються: JPG, PNG, PDF',
      uploadFailed: 'Помилка завантаження. Спробуйте ще раз',
      analysisFailed: 'Помилка аналізу. Спробуйте ще раз',
    },
  },

  // Pricing Page
  pricing: {
    title: 'Тарифи',
    subtitle: 'Оберіть план, який підходить вашому бізнесу',
    monthly: 'Щомісяця',
    yearly: 'Щорічно',
    yearlyDiscount: 'Економія 20%',
    plans: [
      {
        name: 'Starter',
        price: '0',
        period: 'безкоштовно',
        description: 'Для знайомства з сервісом',
        features: [
          '3 перевірки на місяць',
          'Базовий звіт',
          'Email підтримка',
        ],
        cta: 'Почати безкоштовно',
        popular: false,
      },
      {
        name: 'Professional',
        price: '990',
        period: 'грн/міс',
        description: 'Для малого бізнесу',
        features: [
          '50 перевірок на місяць',
          'Детальний PDF-звіт',
          'Історія перевірок',
          'Пріоритетна підтримка',
          'API доступ',
        ],
        cta: 'Обрати Professional',
        popular: true,
      },
      {
        name: 'Enterprise',
        price: '2990',
        period: 'грн/міс',
        description: 'Для великих компаній',
        features: [
          'Необмежені перевірки',
          'Детальний PDF-звіт',
          'Історія перевірок',
          'Пріоритетна підтримка 24/7',
          'API доступ',
          'Генератор етикеток',
          'Персональний менеджер',
        ],
        cta: "Зв'язатися з нами",
        popular: false,
      },
    ],
  },

  // Generator Page (Coming Soon)
  generator: {
    title: 'Генератор етикеток',
    subtitle: 'Скоро',
    description: 'Автоматичне створення тексту етикетки, що відповідає всім вимогам законодавства.',
    notify: 'Отримати сповіщення',
    emailPlaceholder: 'Ваш email',
  },

  // Editor Page (Coming Soon)  
  editor: {
    title: 'Графічний редактор',
    subtitle: 'Скоро',
    description: 'Створюйте дизайн етикетки онлайн з готовими шаблонами та автоматичною перевіркою.',
    notify: 'Отримати сповіщення',
  },

  // Footer
  footer: {
    description: 'Автоматична перевірка етикеток дієтичних добавок на відповідність законодавству України.',
    product: {
      title: 'Продукт',
      links: [
        { label: 'Перевірка етикеток', href: '/checker' },
        { label: 'Генератор', href: '/generator' },
        { label: 'Тарифи', href: '/pricing' },
      ],
    },
    support: {
      title: 'Підтримка',
      links: [
        { label: 'Як це працює', href: '/#how-it-works' },
        { label: 'FAQ', href: '#' },
        { label: "Зв'язатися з нами", href: '#' },
      ],
    },
    legal: {
      title: 'Правова інформація',
      links: [
        { label: 'Умови використання', href: '#' },
        { label: 'Політика конфіденційності', href: '#' },
      ],
    },
    copyright: '© 2025 LabelCheck UA. Всі права захищені.',
  },

  // Common
  common: {
    loading: 'Завантаження...',
    error: 'Помилка',
    success: 'Успішно',
    cancel: 'Скасувати',
    confirm: 'Підтвердити',
    back: 'Назад',
    next: 'Далі',
    submit: 'Надіслати',
    comingSoon: 'Скоро',
    learnMore: 'Дізнатися більше',
  },

  // Regulatory References
  regulatory: {
    laws: [
      {
        id: 'law-4122',
        name: 'Закон України №4122-IX',
        description: 'Про дієтичні добавки',
        penalty: 640000,
      },
      {
        id: 'law-2639',
        name: 'Закон України №2639-VIII',
        description: 'Про інформацію для споживачів',
        penalty: 62600,
      },
      {
        id: 'order-1114',
        name: 'Наказ МОЗ №1114',
        description: 'Гігієнічні вимоги до дієтичних добавок',
        penalty: 640000,
      },
    ],
  },
} as const;

export type Content = typeof content;


