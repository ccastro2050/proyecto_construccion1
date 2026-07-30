"""
productosporfactura_controller.py — Controller para la tabla productosporfactura.

Tabla de detalle de factura con PK compuesta (fknumfactura, fkcodproducto).

Endpoints:
- GET    /api/productosporfactura/                          → Listar detalles
- GET    /api/productosporfactura/factura/{fknumfactura}     → Detalles de una factura
- POST   /api/productosporfactura/                          → Crear detalle
- DELETE /api/productosporfactura/{fknumfactura}/{fkcodproducto} → Eliminar detalle
"""

from fastapi import APIRouter, HTTPException, Query, Response

from models.productosporfactura import ProductosPorFactura
from servicios.fabrica_repositorios import crear_servicio_productosporfactura


router = APIRouter(prefix="/api/productosporfactura", tags=["ProductosPorFactura"])


# =========================================================================
# GET /api/productosporfactura/ — Listar todos los detalles
# =========================================================================

@router.get("/")
async def listar_detalles(
    esquema: str | None = Query(default=None),
    limite: int | None = Query(default=None)
):
    """Lista todos los detalles de facturas."""
    try:
        servicio = crear_servicio_productosporfactura()
        filas = await servicio.listar(esquema, limite)

        if len(filas) == 0:
            return Response(status_code=204)

        return {
            "tabla": "productosporfactura",
            "total": len(filas),
            "datos": filas
        }

    except ValueError as ex:
        raise HTTPException(status_code=400, detail={
            "estado": 400, "mensaje": "Parámetros inválidos.", "detalle": str(ex)
        })
    except Exception as ex:
        raise HTTPException(status_code=500, detail={
            "estado": 500, "mensaje": "Error interno del servidor.", "detalle": str(ex)
        })


# =========================================================================
# GET /api/productosporfactura/factura/{fknumfactura} — Detalles de una factura
# =========================================================================

@router.get("/factura/{fknumfactura}")
async def obtener_por_factura(
    fknumfactura: int,
    esquema: str | None = Query(default=None)
):
    """Obtiene los productos de una factura específica."""
    try:
        servicio = crear_servicio_productosporfactura()
        filas = await servicio.obtener_por_factura(fknumfactura, esquema)

        if len(filas) == 0:
            raise HTTPException(status_code=404, detail={
                "estado": 404,
                "mensaje": f"No se encontraron productos para factura {fknumfactura}"
            })

        return {
            "tabla": "productosporfactura",
            "filtro": f"fknumfactura = {fknumfactura}",
            "total": len(filas),
            "datos": filas
        }

    except HTTPException:
        raise
    except Exception as ex:
        raise HTTPException(status_code=500, detail={
            "estado": 500, "mensaje": "Error interno del servidor.", "detalle": str(ex)
        })


# =========================================================================
# POST /api/productosporfactura/ — Crear detalle
# =========================================================================

@router.post("/")
async def crear_detalle(
    detalle: ProductosPorFactura,
    esquema: str | None = Query(default=None)
):
    """Crea un nuevo detalle de factura. Valida con el modelo Pydantic."""
    try:
        datos = detalle.model_dump()
        servicio = crear_servicio_productosporfactura()
        creado = await servicio.crear(datos, esquema)

        if creado:
            return {
                "estado": 200,
                "mensaje": "Detalle de factura creado exitosamente.",
                "datos": datos
            }
        else:
            raise HTTPException(status_code=500, detail={
                "estado": 500, "mensaje": "No se pudo crear el detalle."
            })

    except HTTPException:
        raise
    except ValueError as ex:
        raise HTTPException(status_code=400, detail={
            "estado": 400, "mensaje": "Datos inválidos.", "detalle": str(ex)
        })
    except Exception as ex:
        raise HTTPException(status_code=500, detail={
            "estado": 500, "mensaje": "Error interno del servidor.", "detalle": str(ex)
        })


# =========================================================================
# DELETE /api/productosporfactura/{fknumfactura}/{fkcodproducto}
# =========================================================================

@router.delete("/{fknumfactura}/{fkcodproducto}")
async def eliminar_detalle(
    fknumfactura: int,
    fkcodproducto: str,
    esquema: str | None = Query(default=None)
):
    """Elimina un detalle de factura por su PK compuesta."""
    try:
        servicio = crear_servicio_productosporfactura()
        filas = await servicio.eliminar(fknumfactura, esquema)

        if filas > 0:
            return {
                "estado": 200,
                "mensaje": "Detalle de factura eliminado exitosamente.",
                "filtro": f"fknumfactura = {fknumfactura}, fkcodproducto = {fkcodproducto}",
                "filasEliminadas": filas
            }
        else:
            raise HTTPException(status_code=404, detail={
                "estado": 404,
                "mensaje": f"No existe detalle con fknumfactura = {fknumfactura}"
            })

    except HTTPException:
        raise
    except Exception as ex:
        raise HTTPException(status_code=500, detail={
            "estado": 500, "mensaje": "Error interno del servidor.", "detalle": str(ex)
        })
