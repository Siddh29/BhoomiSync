export default function SectionHeader({title,description,children,actions}) {
  return <div className="section-header"><div><h2>{title}</h2>{description && <p>{description}</p>}</div>{(children||actions) && <div className="section-actions">{children||actions}</div>}</div>;
}
