import { useEffect, useState } from "react";

export default function App() {
  const tg = window.Telegram?.WebApp;
  const [catalog, setCatalog] = useState([]);
  const [basket, setBasket] = useState([]);
  const [quiz, setQuiz] = useState([]);
  const [step, setStep] = useState("slides");

  useEffect(() => {
    tg?.expand();
    fetch("/api/catalog").then(r => r.json()).then(setCatalog);
    fetch("/api/quiz").then(r => r.json()).then(setQuiz);
  }, []);

  const submitMission = async () => {
    const params = new URLSearchParams(window.location.search);
    const city = params.get("city") || "spb";
    const payload = { user_id: tg?.initDataUnsafe?.user?.id || 0, look_items: basket, city };
    const r = await fetch("/api/mission/submit", { method:"POST", headers:{ "Content-Type":"application/json" }, body: JSON.stringify(payload) });
    const data = await r.json();
    tg?.sendData(JSON.stringify({ type:"mission_done", coupon: data.coupon }));
    tg?.close();
  };

  const Slide = ({title, text, img}) => (
    <div style={{ border:"1px solid #e5e5e5", borderRadius:16, padding:16, marginBottom:12 }}>
      <h3 style={{ marginTop:0 }}>{title}</h3>
      {img ? <img alt="" src={img} style={{ width:"100%", borderRadius:12, margin:"8px 0" }}/> : null}
      <p style={{ margin:0, lineHeight:1.4 }}>{text}</p>
    </div>
  );

  const slides = [
    { title: "Типы фигуры", text: "Песочные часы, Груша, Прямоугольник, Перевернутый треугольник, Яблоко. Задача стилиста — подчеркнуть достоинства и уравновесить пропорции.", img: "/img/body_types.png" },
    { title: "Песочные часы", text: "Подчеркиваем талию: приталенные платья, ремни, высокие посадки. Избегаем бесформенных оверсайзов." },
    { title: "Груша", text: "Балансируем верх и низ: акцентные плечи, светлый верх + тёмный низ, А-силуэт." }
  ];

  if (step === "slides") {
    return (
      <div style={{ padding: 16 }}>
        <h2>Урок 1: Определяем тип фигуры</h2>
        {slides.map((s, i) => <Slide key={i} {...s} />)}
        <button onClick={() => setStep("quiz")} style={{ marginTop: 8 }}>Перейти к квизу</button>
      </div>
    );
  }

  if (step === "quiz") {
    return (
      <div style={{ padding: 16 }}>
        <h2>Квиз</h2>
        {quiz.map((q) => (
          <div key={q.id} style={{ border:"1px solid #eee", borderRadius:12, padding:12, marginBottom:12 }}>
            <div style={{ fontWeight:600, marginBottom:8 }}>{q.q}</div>
            <div style={{ display:"grid", gap:8 }}>
              {q.a.map((opt, oi) => (
                <button key={oi} onClick={() => alert(q.correct===oi ? "Верно!" : ("Подсказка: " + q.tip))}>{opt}</button>
              ))}
            </div>
          </div>
        ))}
        <button onClick={() => setStep("mission")} style={{ marginTop: 8 }}>Дальше → Практика</button>
      </div>
    );
  }

  return (
    <div style={{ padding: 16 }}>
      <h2>Практика: собери лук</h2>
      <div style={{ display:"grid", gap:12 }}>
        {catalog.map(item => (
          <div key={item.id} style={{ border:"1px solid #e5e5e5", borderRadius:12, padding:12 }}>
            <div style={{ fontWeight:600 }}>{item.title}</div>
            <div>{item.price} ₽</div>
            <button onClick={() => setBasket(v => v.includes(item.id) ? v : [...v, item.id])}>Добавить</button>
          </div>
        ))}
      </div>
      <div style={{ marginTop:16 }}>
        <div>Выбрано: {basket.length} шт.</div>
        <button disabled={!basket.length} onClick={submitMission}>Готово → получить купон</button>
      </div>
    </div>
  );
}
