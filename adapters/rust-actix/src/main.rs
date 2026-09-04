use actix_web::{App, HttpServer};
use cmb_boundary_actix::configure;

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    HttpServer::new(|| App::new().configure(configure))
        .bind(("127.0.0.1", 8000))?
        .run()
        .await
}
