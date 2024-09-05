import ContentLoader from "react-content-loader"

const Skeleton = (props: any) => (
    <ContentLoader
        speed={2}
        width={292}
        height={445}
        viewBox="0 0 292 445"
        backgroundColor="#f3f3f3"
        foregroundColor="#ecebeb"
        {...props}
    >
        <rect x="15" y="10" rx="12" ry="12" width="260" height="260" />
        <rect x="15" y="290" rx="12" ry="12" width="260" height="60" />
        <rect x="133" y="385" rx="12" ry="12" width="142" height="40" />
        <rect x="15" y="390" rx="12" ry="12" width="70" height="30" />
    </ContentLoader>
)

export default Skeleton