# Sistema de pedidos - Cafeteria UTEC (web.py basico)
# 2 filas FIFO: normal y prioritaria. La prioritaria siempre se atiende primero.
import web
from collections import deque

urls = (
    '/', 'Index',
    '/registrar', 'Registrar',
    '/preparar', 'Preparar',
    '/siguiente', 'Siguiente',
    '/pendientes', 'Pendientes',
    '/estadisticas', 'Estadisticas',
    '/cancelar', 'Cancelar',
)

app = web.application(urls, globals())
render = web.template.render('templates', base='layout')

# ---- "Base de datos" en memoria ----
fila_normal = deque()
fila_prioritaria = deque()
preparados = []
cancelados = []
contador = {'id': 0}


def siguiente_pedido():
    """Devuelve (sin sacar) el siguiente pedido: prioritaria primero."""
    if fila_prioritaria:
        return fila_prioritaria[0]
    if fila_normal:
        return fila_normal[0]
    return None


class Index:
    def GET(self):
        return render.index()


class Registrar:
    def GET(self):
        return render.registrar(None)

    def POST(self):
        f = web.input(cliente='', producto='', cantidad='1', tipo='normal', tiempo='5')
        try:
            cantidad = int(f.cantidad)
            tiempo = int(f.tiempo)
            if not f.cliente.strip() or not f.producto.strip() or cantidad < 1 or tiempo < 1:
                raise ValueError
        except ValueError:
            return render.registrar('Datos invalidos, revisa el formulario.')
        contador['id'] += 1
        pedido = {
            'id': contador['id'],
            'cliente': f.cliente.strip(),
            'producto': f.producto.strip(),
            'cantidad': cantidad,
            'tipo': 'prioritario' if f.tipo == 'prioritario' else 'normal',
            'tiempo': tiempo,
        }
        if pedido['tipo'] == 'prioritario':
            fila_prioritaria.append(pedido)
        else:
            fila_normal.append(pedido)
        raise web.seeother('/pendientes')


class Preparar:
    def GET(self):
        return render.preparar(siguiente_pedido(), None)

    def POST(self):
        if fila_prioritaria:
            pedido = fila_prioritaria.popleft()
        elif fila_normal:
            pedido = fila_normal.popleft()
        else:
            return render.preparar(None, None)
        preparados.append(pedido)
        return render.preparar(siguiente_pedido(), pedido)


class Siguiente:
    def GET(self):
        return render.siguiente(siguiente_pedido())


class Pendientes:
    def GET(self):
        return render.pendientes(list(fila_prioritaria), list(fila_normal))


class Cancelar:
    def GET(self):
        return render.cancelar(None)

    def POST(self):
        f = web.input(id='')
        try:
            pid = int(f.id)
        except ValueError:
            return render.cancelar('Escribe un numero de pedido valido.')
        for fila in (fila_prioritaria, fila_normal):
            for p in fila:
                if p['id'] == pid:
                    fila.remove(p)
                    cancelados.append(p)
                    return render.cancelar('Pedido #%d cancelado.' % pid)
        return render.cancelar('No existe el pedido #%d en las filas pendientes.' % pid)


class Estadisticas:
    def GET(self):
        total = len(preparados) + len(cancelados) + len(fila_normal) + len(fila_prioritaria)
        prom = (sum(p['tiempo'] for p in preparados) / len(preparados)) if preparados else 0
        datos = {
            'Pedidos registrados': total,
            'Pendientes normales': len(fila_normal),
            'Pendientes prioritarios': len(fila_prioritaria),
            'Pedidos preparados': len(preparados),
            'Pedidos cancelados': len(cancelados),
            'Unidades preparadas': sum(p['cantidad'] for p in preparados),
            'Tiempo promedio de preparacion (min)': round(prom, 2),
        }
        return render.estadisticas(datos)


if __name__ == '__main__':
    app.run()
