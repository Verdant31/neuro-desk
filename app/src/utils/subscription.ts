import type { AuthResponse } from '@/types'

export function validateSubscription(authResponse: AuthResponse): boolean {
  const status = authResponse.subscription_status
  return status === 'active' || status === 'trialing'
}

export function getSubscriptionStatusMessage(
  authResponse: AuthResponse,
): string {
  switch (authResponse.subscription_status) {
    case 'active':
      return 'Assinatura ativa'
    case 'trialing':
      return 'Período de teste'
    case 'past_due':
      return 'Pagamento pendente'
    case 'canceled':
      return 'Assinatura cancelada'
    case 'incomplete':
      return 'Pagamento incompleto'
    case 'incomplete_expired':
      return 'Pagamento expirado'
    case 'unpaid':
      return 'Pagamento não realizado'
    default:
      return 'Status desconhecido'
  }
}
