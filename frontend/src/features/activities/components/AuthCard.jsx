export default function AuthCard({ title, subtitle, children, footer }) {
  return (
    <>
      <div>
        <div>
          <h2>{title}</h2>
          {subtitle ? <p>{subtitle}</p> : null}
        </div>

        {children}

        {footer ? <div>{footer}</div> : null}
      </div>
    </>
  );
}
