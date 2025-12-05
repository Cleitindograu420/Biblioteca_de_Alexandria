import { useEffect, useState } from "react";
import axios from "axios";

export default function Login() {
  const [usuario, setUsuario] = useState({});

  useEffect(() => {
    axios.get("http://localhost:8000/api/usuario/")
      .then(res => setUsuario(res.data));
  }, []);

  return (
    <div>
      <h1>Bem-vindo {usuario.nome}</h1>
    </div>
  );
}
