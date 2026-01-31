c----------------------------------------------------------------------
      program testo
      implicit double precision (a-h,o-z)
c----------------------------------------------------------------------
c.....Test the order of Simpson-rule surface integral approximation
c     Integrating function fi = 5x^4 + 5y^4 -3yx^3 + 3xy^3  along line
c     x=0, from y=0 to y=1, using exact and approximate variable value
c     at face centroid
c----------------------------------------------------------------------
c
      fi(x,y) = -2.0*x + 3.0*x**2 - 7.0*x**3 + x**4 + 5.0*y**4
c
      open(unit=1,file='ointegral',form='formatted')
      rewind 1
      write(1,*) '#  dx  sume   sum2   sum4   esume   esum2   esum4'
c
      open(unit=2,file='ointerpol',form='formatted')
      rewind 2
      write(2,*) '#  dx  fiex   cd2   cd4   ecd2   ecd4'

c
      dly=1.0
      dy=2.0*dly
      x0=0.0
c
c.....Test 5 levels of discretization: from dy=1 to dy=0.0625
c     by halving the previous spacing
c
      ny=1
      do k=1,6
        dy=0.5*dy
        dx=dy
        sume=0.0
        sum2=0.0
        sum4=0.0
c
c.....Loop over all faces
c
        do i=1,ny
c
c.....Face centroid "e" and corner ("ne" and "se") coordinates
c
          xf=0.0
          yf=0.5*dy+(i-1)*dy
          yn=yf+0.5*dy
          ys=yf-0.5*dy
c
c.....X-coordinates of cell centroids on the left and on the right
c     (Y-coordinates same as face coordinate)
c
          x1l=-0.5*dx
          x2l=-1.5*dx
          x1r=0.5*dx
          x2r=1.5*dx
c
c.....Exact variable values at neighbor cell centroids
c
          fi1l=fi(x1l,yf)
          fi2l=fi(x2l,yf)
          fi1r=fi(x1r,yf)
          fi2r=fi(x2r,yf)
          fi1ln=fi(x1l,yn)
          fi2ln=fi(x2l,yn)
          fi1rn=fi(x1r,yn)
          fi2rn=fi(x2r,yn)
          fi1ls=fi(x1l,ys)
          fi2ls=fi(x2l,ys)
          fi1rs=fi(x1r,ys)
          fi2rs=fi(x2r,ys)
c
c.....Exact and approximate variable value at face centroid and corners
c
          fifex=fi(x0,yf)
          fifcd2=0.5*(fi1l+fi1r)
          fifcd4=(9.0*fi1l+9.0*fi1r-fi2l-fi2r)/16.0
          finex=fi(x0,yn)
          fincd2=0.5*(fi1ln+fi1rn)
          fincd4=(9.0*fi1ln+9.0*fi1rn-fi2ln-fi2rn)/16.0
          fisex=fi(x0,ys)
          fiscd2=0.5*(fi1ls+fi1rs)
          fiscd4=(9.0*fi1ls+9.0*fi1rs-fi2ls-fi2rs)/16.0
c
c.....Compute contribution to the integral from the face "i" using
c     exact variable values and 2nd and 4th order CD approximations
c
          sume=sume+(finex+fisex+4.0*fifex)*dy/6.0
          sum2=sum2+(fincd2+fiscd2+4.0*fifcd2)*dy/6.0
          sum4=sum4+(fincd4+fiscd4+4.0*fifcd4)*dy/6.0
c
        end do
c
c.....Compute errors: exact integral value is 1.0
c
        esume=abs(1.0-sume)
        esum2=abs(1.0-sum2)
        esum4=abs(1.0-sum4)
c
c.....Write results for gnuplot evaluation - integral approximations
c
        write(1,*) dx,sume,sum2,sum4,esume,esum2,esum4
c
        ny=ny*2
      end do
c
      stop
      end
