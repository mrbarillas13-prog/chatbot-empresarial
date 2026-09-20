import os
import httpx

RESEND_API_KEY = os.getenv("RESEND_API_KEY", "")
FROM_EMAIL = os.getenv("FROM_EMAIL", "TechStore <pedidos@chatbotexpertservice.online>")


def send_order_confirmation(to_email: str, customer_name: str, order_id: str, product_name: str, total: float) -> bool:
    try:
        html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: #1e3a5f; color: white; padding: 20px; text-align: center;">
                <h1>TechStore</h1>
            </div>
            <div style="padding: 30px; background: #f9fafb;">
                <h2 style="color: #1e3a5f;">Pedido Confirmado</h2>
                <p>Hola <strong>{customer_name}</strong>,</p>
                <p>Tu pedido fue recibido exitosamente.</p>
                <div style="background: white; border-radius: 8px; padding: 20px; margin: 20px 0; border: 1px solid #e5e7eb;">
                    <p><strong>Pedido ID:</strong> <code style="background: #f3f4f6; padding: 2px 8px; border-radius: 4px;">{order_id[:8]}...</code></p>
                    <p><strong>Producto:</strong> {product_name}</p>
                    <p><strong>Total:</strong> {total:.2f} EUR</p>
                    <p><strong>Estado:</strong> Pendiente de pago</p>
                </div>
                <p style="color: #6b7280; font-size: 14px;">
                    Para consultar tu pedido, ingresa a chatbotexpertservice.online y pregunta por tu pedido.
                </p>
            </div>
            <div style="background: #1e3a5f; color: white; padding: 15px; text-align: center; font-size: 12px;">
                TechStore - Tu tienda de tecnologia
            </div>
        </div>
        """

        response = httpx.post(
            "https://api.resend.com/emails",
            headers={
                "Authorization": f"Bearer {RESEND_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "from": FROM_EMAIL,
                "to": [to_email],
                "subject": f"Pedido #{order_id[:8]} confirmado - TechStore",
                "html": html
            },
            timeout=10
        )

        if response.status_code == 200:
            print(f"Email enviado a {to_email} - Pedido {order_id[:8]}")
            return True
        else:
            print(f"Error enviando email: {response.status_code} - {response.text}")
            return False

    except Exception as e:
        print(f"Error en send_order_confirmation: {str(e)}")
        return False
